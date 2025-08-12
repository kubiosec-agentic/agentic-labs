## Instal setup scripts
for i in $(seq -w 1 999); do
    cp ./bootstrap/* ../lab${i}*/
done
