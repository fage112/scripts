#!/bin/bash
#检查数据库主从数据复制是否一致
#原理：对比主从服务器每张表的行数
#author: 发哥
#QQ: *******
PATH=/usr/kerberos/sbin:/usr/kerberos/bin:/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/root/bin
export PATH
Today=`date +%Y%m%d`
User='***'
Pwd='*******'
Remote_host=`mysql -e "show slave status\G" | grep Master_Host | awk '{print $2}'`
Master_data=/opt/shell/data/Master_data
Slave_data=/opt/shell/data/Slave_data
if [ ! -d /opt/shell/data ];then
    mkdir -pv /opt/shell/data
fi
get_mysql_talbes(){
    mysql -N -u\'"$User"\' -p"$Pwd" -h "$Remote_host" 1>"$Master_data" << EOF
    use information_schema;
    select a.table_name,a.table_rows from information_schema.tables as a where a.TABLE_SCHEMA = 'abc' order by a.table_rows desc;
EOF
    if [ $? -ne 0 ];then
    #判断是否获取到主服务器的数据
        echo 'Can not connect master mysql server,Plz check the network.'
        exit 6
    fi
    mysql -N 1>"$Slave_data"  << EOF
    use information_schema;
    select a.table_name,a.table_rows from information_schema.tables as a where a.TABLE_SCHEMA = 'abc' order by a.table_rows desc;
EOF
    if [ $? -ne 0 ];then
        #判断是否获取到本地数据库的数据
        echo 'Can not connect local mysql server,Plz check mysql service status.'
        exit 6
    fi
}
#检查mysql帐号是否有mysqldump权限
mysqldump -u *** $Remote_host -p******* abc tb_name > /dev/null 2>&1
if [ $? -ne 0 ];then
    echo "Plz check the Master MySQL server privilege!"
    exit 1
fi
get_mysql_talbes
Mtb_counts=`cat $Master_data | wc -l`
Stb_counts=`cat $Slave_data | wc -l`
if [ $Mtb_counts -ne $Stb_counts ];then
    #判断主数据库和从数据库的表数量是否一致
    while read list;do
        Master_Table_name=`echo $list | awk '{print $1}'`
        a=`cat $Slave_data | grep "\(\<$Master_Table_name\>\)\{1\}[[:space:]]*[[:digit:]]*"`
        if [ "${a}" == '' ];then
            echo "$Master_Table_name is not exist,Restore the table"
            mysqldump -u *** -h $Remote_host -p******* abc $Master_Table_name | mysql abc
        fi
    done < $Master_data
fi
get_mysql_talbes
while read M;do
    #对比每张表行数是否一致
    Mtb_name=`echo $M | awk '{print $1}'`
    Mrows=`echo $M | awk '{print $2}'`
    Stb_name=`cat $Slave_data | grep "\(\<$Mtb_name\>\)\{1\}[[:space:]]*[[:digit:]]*" | awk '{print $1}'`
    Srows=`cat $Slave_data | grep "\(\<$Mtb_name\>\)\{1\}[[:space:]]*[[:digit:]]*" | awk '{print $2}'`
    if [ $Mtb_name == $Stb_name ];then
        #当天的表不校验
        remove_list=`echo $Mtb_name | grep -o ${Today}`
        if [ "${remove_list}" == ${Today} ];then
           continue
        fi
        if [ $Mrows -ne $Srows ];then
            #如果表的行数不一样则清空表，并同步从新同步主服务器的数据
            echo -e "$Mtb_name\tMaster_rows($Mrows)\tSlave_rows($Srows)"
            mysql << EOF
            use abc;
            truncate table $Mtb_name;
EOF
            mysqldump -u *** -h $Remote_host -p******* abc $Mtb_name | mysql abc
            if [ $? -eq 0 ];then
                echo "$Mtb_name is restore success!"
            else
                echo "$Mtb_name is restore failed!"
            fi
        fi
    fi
done < $Master_data