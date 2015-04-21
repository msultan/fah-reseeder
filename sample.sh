#$ -cwd
#$ -S /bin/bash

#$ -j y
#$ -R y
#$ -w e

# email address to send notices to
#$ -M $USER@stanford.edu
#$ -m beas

#$ -pe orte 30

echo "job starting on `date`"
echo ""

echo "purging module environment"
module purge
echo "loading modules..."

# list your module load commands here:
module load mpi

echo "done"
echo ""
module list
echo ""
echo "beginning job on `hostname`"

ipcontroller --ip="*"  &
sleep 5

tmphosts=`mktemp`
awk '{ for (i=0; i < $2; ++i) { print $1} }' $PE_HOSTFILE > $tmphosts

echo ""

mpirun -np $NSLOTS -machinefile $tmphosts --bynode ipengine &
sleep 20
fah_reseeder -d test_proj/ -i False -s 1 -p default

#kill the controller 
kill -9 `cat $HOME/.ipython/profile_default/pid/ipcontroller.pid`
ipcluster stop --profile=default


