# WorkHome
1.进入cd appfront 目录
npm install 安装vue依赖

celery 采坑
https://blog.csdn.net/qq_30242609/article/details/79047660
pip install eventlet
celery -A <mymodule> worker -l info -P eventlet
mac 没有此坑 直接 celery -A <mymodule> worker -l info
远程服务器
安装redis  :  sudo apt-get install redis-server 
redis 开启远程访问:
注释 /etc/redis/redis.conf文件中的   bind 127.0.0.1 ::1 
并修改  protected-mode no  重启redis  /etc/init.d/redis-server restart

virtualbox 共享文件夹
坑：挂载到的文件夹要 设置权限 chom 777 . 
https://blog.csdn.net/yuanguangyu1221/article/details/51870022