

ipcluster start -n 2 &
sleep 10

fah_reseeder -d test_proj/ -i False -s 1

ipcluster stop 
