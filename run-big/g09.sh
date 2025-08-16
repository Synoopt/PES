#!/bin/bash

# 设置环境变量
export GAUSS_SCRDIR=/home/your_username/gaussian/g16/scratch

# 遍历所有输入文件
for input in */*.gjf
do
    # 构建输出文件名
    output="${input%.gjf}.out"
    
    # 确保输入文件和输出文件所在的目录存在并且有正确的权限
    chmod u+rw "${input}"
    sudo chown your_username:your_username "${input}"
    
    # 检查磁盘空间
    if [ $(df -h | grep -w '/' | awk '{print $5}' | sed 's/%//') -gt 90 ]; then
        echo "磁盘空间不足，停止处理 ${input}"
        continue
    fi
    
    # 运行Gaussian
    if g16 < "${input}" > "${output}"
    then
        echo "处理成功：${input} -> ${output}"
    else
        echo "处理失败：${input}" >&2
    fi
done
