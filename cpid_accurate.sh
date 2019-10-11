#!/bin/bash
if [ ! -f mmy_log.gz ];then
    sh cpid_mmy/mmy_download_log.sh &
fi

if [ ! -f ws_log.gz ];then
    sh cpid_ws/ws_download_log.sh &
fi

if [ ! -f bd_log.gz ];then
   sh cpid_bd/bd_download_log.sh &
fi
wait

if [ ! -f ts ];then
    zcat mmy_log.gz |grep ts|grep -w "HIT"|grep -w "edge"|awk '{print $8}'|awk -F"/"  '{print "/"$4"/"$5}' > ts 
    zcat ws_log.gz |grep ts|awk '{print $7}'|awk -F"/" '{print "/"$4"/"$5}' >> ts 
    zcat bd_log.gz |grep -w edge|grep ts|awk '{print $9}' >> ts 
fi

if [ ! -f ts_sort ];then
    cat ts|awk '{a[$1]+=1;}END{for(i in a){print a[i]" "i}}'|sort -t " " -k 1 -n -r  >ts_sort
fi
mysql -h lg_55 -ufidcpidmatch -p"password" \
      -e"select a.fid,b.cpid from epgvideoinfo b inner join epgvideomedia a on a.vid=b.vid where a.type=2 and a.srcfrom=0 and b.sid=0" epgnew >mysql
wait
cat mysql |awk '!a[$1]++{print}' > resualt

cat ts_sort|awk -F"-" '{print $1}'|awk -F"/" '{print $3}'|awk '!a[$1]++{print}' >match_fid
awk 'NR==FNR{a[NR]=$1}NR>FNR{ for( i in a){if(a[i]==$1)print $0 }}' match_fid resualt >rs.txt

cat ts_sort|while read line
do
    fid=`echo $line|awk -F"-" '{print $1}'|awk -F"/" '{print $3}'`
    ts=`echo $line|awk '{print $2}'`
    ts_count=`echo $line|awk '{print $1}'`
    cpid=`cat rs.txt|grep $fid|awk '{print $2}'`
    ts_size=`echo $line|awk -F"-" '{print $5}'|awk -F"." '{print $1}'`
    if [ -n "$cpid" ];then
       if [ ! -f "$cpid" ];then
           touch $cpid
       fi
       echo $cpid" "$ts" "$ts_count" "$ts_size" "$ts_stream >>$cpid
    fi
done
ts_total_stream=0
for i in 100{01..25}
do
   if [ -f $i ];then
       while read line2
       do
           count=`echo $line2|awk '{print $3}'`
           size=`echo $line2|awk '{print $4}'`
           ts_stream=$[$count*$size]
           ts_total_stream=$[$ts_stream+$ts_total_stream]
       done < $i
       echo "{\"$i\":\"$ts_total_stream\"}" >> total_stream
       ts_total_stream=0
   else
       echo "{\"$i\":\"0\"}" >> total_stream
   fi
done
date=`date  +"%Y%m%d" -d  "-1 days"`
if [ ! -d $date ];then
    mkdir $date
fi
mv  rs.txt ts_sort  wget_url_*  *.gz total_stream 100* $date 
