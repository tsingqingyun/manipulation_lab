"""Render recorded actions with clearer cameras; compare every replayed state to the saved trace."""
import hashlib
import json
from pathlib import Path
import shutil
import h5py
import imageio.v2 as imageio
import numpy as np
from scipy.spatial.transform import Rotation
from manipulation_lab.common import DATA, sha256
from manipulation_lab.dataset import initial_state
from manipulation_lab.simulator import create_env, reset_episode, snapshot

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'assignment_solutions_20261013'
A=HERE/'assets'


def camera(env,pos,target,fovy=44):
    raw=env.env
    z=np.array(pos,dtype=float)-target;z/=np.linalg.norm(z)
    x=np.cross([0.,0.,1.],z);x/=np.linalg.norm(x);y=np.cross(z,x)
    q=Rotation.from_matrix(np.column_stack([x,y,z])).as_quat()
    i=raw.sim.model.camera_name2id('agentview')
    assert raw.sim.model.cam_bodyid[i]==0, 'This helper expects a world-fixed camera'
    raw.sim.model.cam_pos[i]=pos;raw.sim.model.cam_quat[i]=q[[3,0,1,2]];raw.sim.model.cam_fovy[i]=fovy
    # Update only camera transforms. An extra mj_forward would touch contact
    # solver caches and perturb the recorded-action replay near grasp contact.
    raw.sim.data.cam_xpos[i]=pos
    raw.sim.data.cam_xmat[i]=np.column_stack([x,y,z]).ravel()


def render(env,close=False):
    if close:camera(env,[.57,-.49,1.27],[.035,-.34,.905],38)
    else:camera(env,[1.,0.,1.52],[.03,0.,.91],44)
    return env.render(mode='rgb_array',width=960,height=640 if close else 540)


def main():
    if (HERE/'replay_provenance.json').exists():raise FileExistsError('Preserve existing replay assets')
    d=json.loads((OLD/'results.json').read_text())
    shutil.copyfile(OLD/'results.json',HERE/'results.json')
    shutil.copyfile(OLD/'slides.json',HERE/'reference_notes.json')
    shutil.copyfile(OLD/'solution_execution.json',HERE/'solution_execution.json')
    for p in (OLD/'evidence').iterdir():
        if p.is_file():shutil.copyfile(p,HERE/'evidence'/p.name)
    provenance={'kind':'Saved-action replay for presentation cameras','new_training_runs':0,'new_policy_evaluations':0,
                'dataset_sha256':sha256(DATA),'sources':{},'cases':{},'cameras':{
                'overview':{'position':[1.,0.,1.52],'target':[.03,0.,.91],'fovy':44,'resolution':[960,540]},
                'detail':{'position':[.57,-.49,1.27],'target':[.035,-.34,.905],'fovy':38,'resolution':[960,640]}}}
    with h5py.File(DATA) as f:meta=json.loads(f['data'].attrs['env_args'])
    env=create_env(meta,video=True)
    try:
        for label,end,steps in [('failure',101,[0,45,53,56,57,65,85,101]),('success',141,[1,41,61,89,121,141])]:
            trace=np.load(OLD/'evidence'/f'{label}_trace.npz');case=d[label+'_episode']
            obs=reset_episode(env,DATA,case['source_episode'],case['seed'])
            errors={k:0. for k in ['object_position','eef_position','gripper_qpos','gripper_width']}
            bool_equal=True
            def compare(t):
                nonlocal bool_equal
                st=snapshot(env,obs)
                for k in errors:errors[k]=max(errors[k],float(np.max(np.abs(np.asarray(st[k])-trace[k][t]))))
                for k in ['gripper_contact','inside_target_margin','environment_success']:bool_equal &= bool(st[k])==bool(trace[k][t])
            compare(0)
            imageio.imwrite(A/f'{label}_start.png',render(env))
            frame_steps=[]
            with imageio.get_writer(A/f'{label}_hd.mp4',fps=5,codec='libx264',pixelformat='yuv420p',quality=8) as video:
                for t,action in enumerate(trace['actions'][:end],1):
                    obs,_,_,_=env.step(action);compare(t)
                    if t in steps:
                        imageio.imwrite(A/f'{label}_{t:03d}.png',render(env))
                        if label=='failure':imageio.imwrite(A/f'detail_{t:03d}.png',render(env,True))
                    if t%2==1:
                        video.append_data(render(env));frame_steps.append(t)
            assert max(errors.values())<1e-6 and bool_equal,(label,errors,bool_equal)
            provenance['cases'][label]={'source_episode':case['source_episode'],'seed':case['seed'],'source_case':case['episode_id'],
                'replayed_steps':end,'trace_length':len(trace['actions']),'max_absolute_state_errors':errors,'all_logged_booleans_match':bool_equal,
                'still_steps':[t for t in steps if t>0],'video_control_steps':frame_steps,'video_fps':5,
                'playback':'half speed: 20 Hz control / stride 2 / 5 fps playback'}
            provenance['sources'][f'evidence/{label}_trace.npz']=sha256(OLD/'evidence'/f'{label}_trace.npz')
            print(label,errors,'booleans match:',bool_equal,flush=True)
        with h5py.File(DATA) as f:
            demo=f['data/demo_0']
            (HERE/'evidence/demo_0_actions.json').write_text(json.dumps({'episode':'demo_0','source':'data/low_dim_v15.hdf5:data/demo_0/actions','actions':demo['actions'][:].tolist()},indent=2)+'\n')
            env.reset_to(initial_state(DATA,'demo_0'))
            for t in [0,40,58,82,116]:
                env.reset_to({'states':demo['states'][t]})
                imageio.imwrite(A/f'demo_{t:03d}.png',render(env))
        provenance['demonstration']={'episode':'demo_0','states':[0,40,58,82,116],'method':'Restore recorded HDF5 simulator states'}
    finally:env.env.close()
    provenance['asset_sha256']={p.name:sha256(p) for p in A.iterdir()}
    provenance['video_encoded_resolution']=[960,544]
    provenance['video_encoder_note']='FFmpeg expands 960x540 to 960x544 for macroblock compatibility; physical state is unchanged.'
    (HERE/'replay_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')


if __name__=='__main__':main()
