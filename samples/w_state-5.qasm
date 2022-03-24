OPENQASM 2.0;
include "qelib1.inc";
qreg q[5];
creg c[5];
sx q[0];
rz(pi/4) q[0];
sx q[0];
sx q[1];
rz(0.61547970867038737) q[1];
sx q[1];
sx q[2];
rz(pi/6) q[2];
sx q[2];
sx q[3];
rz(0.46364760900080615) q[3];
sx q[3];
x q[4];
cx q[4],q[3];
sx q[3];
rz(0.46364760900080615) q[3];
sx q[3];
cx q[3],q[2];
sx q[2];
rz(pi/6) q[2];
sx q[2];
cx q[2],q[1];
sx q[1];
rz(0.61547970867038693) q[1];
sx q[1];
cx q[1],q[0];
sx q[0];
rz(pi/4) q[0];
sx q[0];
cx q[3],q[4];
cx q[2],q[3];
cx q[1],q[2];
cx q[0],q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
measure q[4] -> c[4];
