"""One nonretry formal child; scoped resource evidence. Stdlib only."""
from pathlib import Path
from datetime import datetime,timezone
import subprocess,sys,os,time,json,resource
O=Path(__file__).resolve().parent;D=O.parent
assert len(sys.argv)==2 and not (O/'formal-started.lock').exists()
def save(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2,ensure_ascii=False);f.write('\n')
def utc():return datetime.now(timezone.utc).isoformat()
env={'PATH':'/usr/bin:/bin:/usr/sbin:/sbin','LANG':'en_US.UTF-8'}
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):env[k]='2'
env['PYTHONDONTWRITEBYTECODE']='1'
cmd=[sys.executable,'-I','-B',str(O/'accounting.py'),'formal','--go',sys.argv[1]]
started=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN);startUTC=utc();peak=0;reason=None
save(O/'formal-command.started.json',{'UTC':startUTC,'command':cmd,'supervisor_PID':os.getpid(),'thread_limits':{k:env[k] for k in env if k.endswith('NUM_THREADS') or k=='VECLIB_MAXIMUM_THREADS'}})
with (O/'formal.stdout.txt').open('x') as out,(O/'formal.stderr.txt').open('x') as err:
 p=subprocess.Popen(cmd,env=env,stdout=out,stderr=err)
 while p.poll() is None:
  ps=subprocess.run(['/bin/ps','-o','rss=','-p',str(p.pid)+','+str(os.getpid())],capture_output=True,text=True)
  peak=max(peak,sum(int(x) for x in ps.stdout.split())*1024)
  disk=sum(x.stat().st_size for x in O.iterdir() if x.is_file())
  if time.monotonic()-started>60:reason='COMPUTE_TIME_LIMIT'
  elif peak>536870912:reason='MEMORY_LIMIT'
  elif disk>4194304:reason='NEW_EXECUTE_DISK_LIMIT'
  elif datetime.now(timezone.utc)>=datetime.fromisoformat('2026-10-19T19:05:30+00:00'):reason='WORK_DEADLINE'
  if reason:p.terminate();break
  time.sleep(.01)
 try:code=p.wait(timeout=3)
 except subprocess.TimeoutExpired:p.kill();code=p.wait();reason=reason or 'TERMINATION_TIMEOUT'
after=resource.getrusage(resource.RUSAGE_CHILDREN)
child_peak=after.ru_maxrss*(1024 if sys.platform.startswith('linux') else 1)
receipt={'start_UTC':startUTC,'end_UTC':utc(),'command':cmd,'worker_PID':p.pid,'supervisor_PID':os.getpid(),'exit_code':code,'stop_reason':reason,'wall_seconds':time.monotonic()-started,'children_user_seconds':after.ru_utime-before.ru_utime,'children_system_seconds':after.ru_stime-before.ru_stime,'peak_worker_plus_supervisor_RSS_bytes_sampled':peak,'child_max_RSS_bytes':child_peak,'new_execute_disk_bytes':sum(x.stat().st_size for x in O.iterdir() if x.is_file()),'thread_limit':2,'stdlib_worker_single_thread':True,'no_live_worker':p.poll() is not None,'formal_lock_exists':(O/'formal-started.lock').exists()}
save(O/'formal-command.receipt.json',receipt);print(json.dumps(receipt));sys.exit(code or (1 if reason else 0))
