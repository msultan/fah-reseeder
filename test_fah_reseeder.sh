

ipcluster start -n 2 &
sleep 10

fah_reseeder -d test_proj/  -s 1

ipcluster stop 
