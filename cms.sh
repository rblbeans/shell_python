#!/bin/bash
cat cname.txt|while read cname
do
file="$cname/$cname.txt"
total_http=`cat $file|grep -v "^#"|wc -l`
first_ts=`cat $file|grep -v "^#"|sed -n "1"p''`
wget $first_ts -O 1.ts
for((i=2;i<$total_http+1;i++))
do
    http=`cat $file|grep -v "^#"|sed -n "$i"'p'`
    wget $http -O ${i}.ts
    cat $[i-1].ts ${i}.ts > a.ts
    mv a.ts $[i].ts 
    rm -f $[i-1].ts
done
mv $[i-1].ts $cname/${cname}.ts
done
