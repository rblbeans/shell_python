#!/bin/bash
function read_dir(){
    for file in `ls $1`
    do
        if [ -d $1"/"$file ] 
        then
            read_dir $1"/"$file
        else
            echo $1"/"$file >> dir_file
        fi
    done
}
function md5(){
    for i in {3..7}
    do
       dpath="/home/media/JMFW/NEWCPS/2019/0$i"
       read_dir $dpath
       for j in `cat dir_file`
       do
           md5sum $j >> md5_file
       done
    done
}

function cdnio(){
    md5
    cat md5_file|while read line
    do
        md5f=`echo "$line|awk '{print $1}'"`
        file=`echo "$line|awk '{print $2}'"`
        cdnio3 upload 42.62.117.54 6388 $file 0 0 $md5f
    done
}
cdnio
