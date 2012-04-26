
x = 0
for fname in `ls -1`; do
    x = $((x+1))
    Y = $(($x % 11))
    X = $(($x / 11))
    cp $fname 4-$y-$x.png
done
