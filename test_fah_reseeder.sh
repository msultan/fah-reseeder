

ipcluster start -n 2 &
sleep 10

fah_reseeder -d test_proj/ -i False -s 1 -t test_proj/topologies/

ipcluster stop 
