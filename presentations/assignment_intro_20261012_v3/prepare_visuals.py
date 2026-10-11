"""Recover clear visual evidence without retraining or choosing new rollout cases."""
import json
import hashlib
import shutil
from pathlib import Path
import h5py
import imageio.v2 as imageio
import numpy as np
import torch
from manipulation_lab.common import DATA, policy_observation
from manipulation_lab.dataset import initial_state
from manipulation_lab.simulator import create_env, reset_episode, snapshot
from manipulation_lab.policy import load_policy

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
A=HERE/'assets'
RUN=ROOT/'outputs/teaching_acceptance_20261012_v1/groups/group_01/20261011T163325Z_131cb6f3'
EXP=RUN/'experiment_163342_eb82ae'
EVAL=EXP/'lr_a/evaluation'


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    if (HERE/'visual_provenance.json').exists(): raise FileExistsError('Preserve the existing verified assets')
    torch.set_num_threads(2)
    summary=json.loads((EVAL/'summary.json').read_text())
    sources=[EVAL/'summary.json',EVAL/'standard_00.npz',EVAL/'standard_01.npz',EVAL/'shifted_01.npz']
    result={'kind':'presentation-only evidence recovery','new_policy_rollouts':0,'new_training_runs':0}
    with h5py.File(DATA) as f: meta=json.loads(f['data'].attrs['env_args'])
    env=create_env(meta,video=True)
    try:
        case=next(e for e in summary['episodes'] if e['episode_id']=='standard_00')
        obs=reset_episode(env,DATA,case['source_episode'],case['seed'])
        trace=np.load(EVAL/'standard_00.npz')
        errors={k:0.0 for k in ['object_position','eef_position','gripper_width']}
        for t,action in enumerate(trace['actions'][:81],1):
            obs,_,_,_=env.step(action);state=snapshot(env,obs)
            for k in errors:errors[k]=max(errors[k],float(np.abs(np.asarray(state[k])-trace[k][t]).max()))
            if t in [1,41,81]:imageio.imwrite(A/f'failure_hd_{t:03d}.png',env.render(mode='rgb_array',width=768,height=768))
        assert max(errors.values())<1e-6,errors
        result['failure_replay']={'case':'standard_00','steps':81,'max_absolute_state_errors':errors,'frame_steps':[1,41,81]}
        pairs=[]
        for condition in ['standard','shifted']:
            case=next(e for e in summary['episodes'] if e['episode_id']==condition+'_01')
            obs=reset_episode(env,DATA,case['source_episode'],case['seed'],shift=(.04,0) if condition=='shifted' else (0,0))
            state=snapshot(env,obs);recorded=np.load(EVAL/(case['episode_id']+'.npz'))
            error=max(float(np.abs(np.asarray(state[k])-recorded[k][0]).max()) for k in ['object_position','eef_position','gripper_width'])
            assert error<1e-6,error
            imageio.imwrite(A/f'{condition}_start.png',env.render(mode='rgb_array',width=768,height=768))
            pairs.append({'case':case['episode_id'],'source_episode':case['source_episode'],'seed':case['seed'],
                          'object_position':state['object_position'].tolist(),'max_state_error':error})
        result['paired_starts']=pairs
        # One fixed recorded observation, not a closed-loop outcome comparison.
        episode,step='demo_0',40
        env.reset_to(initial_state(DATA,episode))
        with h5py.File(DATA) as f:
            d=f['data'][episode]
            stored={k:d['obs'][k][step] for k in ['robot0_eef_pos','robot0_eef_quat','robot0_gripper_qpos','object']}
            expert=d['actions'][step]
            obs=env.reset_to({'states':d['states'][step]})
        selected,expected=policy_observation(obs),policy_observation(stored)
        err=max(float(np.abs(selected[k]-expected[k]).max()) for k in expected)
        assert err<1e-5,err
        imageio.imwrite(A/'demonstration_state.png',env.render(mode='rgb_array',width=768,height=768))
    finally:env.env.close()
    checkpoint=EXP/'lr_a/training/student_policy.pth'
    policy,_=load_policy(checkpoint,device='cpu');policy.start_episode()
    predicted=np.asarray(policy(expected))
    assert predicted.shape==expert.shape==(7,)
    comparison={'episode':episode,'recorded_step':step,'policy_role':'student','variant':'lr_a',
                'checkpoint_sha256':sha(checkpoint),'expert_action':expert.tolist(),'predicted_action':predicted.tolist(),
                'squared_error_per_component':((predicted-expert)**2).tolist(),
                'mean_squared_error':float(np.mean((predicted-expert)**2)),
                'same_observation_render_error':err,
                'interpretation':'Single fixed example on a recorded demonstration state; not held-out policy success or causal explanation.',
                'normalization':'RolloutPolicy applies the checkpoint training-only statistics to the raw observation.'}
    (A/'action_comparison.json').write_text(json.dumps(comparison,indent=2)+'\n')
    demo=RUN/'demonstration_163326_30827c'
    source_provenance=json.loads((demo/'provenance.json').read_text())
    assert source_provenance['episode']=='demo_0'
    shutil.copyfile(demo/'demonstration.mp4',A/'human_demonstration.mp4')
    r=imageio.get_reader(A/'human_demonstration.mp4');imageio.imwrite(A/'human_poster.png',r.get_data(20));metadata=r.get_meta_data();r.close()
    result['human_demonstration']={'source':source_provenance,'duration_seconds':metadata['duration'],'copied_bytes':True}
    result['action_comparison']=comparison
    sources += [checkpoint,demo/'demonstration.mp4',demo/'provenance.json']
    result['sources']=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sources]
    result['new_asset_sha256']={p.name:sha(p) for p in A.iterdir() if p.name.startswith(('failure_hd','standard_start','shifted_start','demonstration_state','human_','action_comparison'))}
    (HERE/'visual_provenance.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'failure_replay_errors':errors,'single_state_mse':comparison['mean_squared_error'],'human_video_seconds':metadata['duration']}),flush=True)


if __name__=='__main__':main()
