# PES 项目 - 势能面计算工具包

## 概述

PES（Potential Energy Surface）项目是一个用于计算三原子系统势能面的综合工具包，支持Gaussian、CP2K和Quantum ESPRESSO三种量子化学软件包。本项目提供完整的输入文件生成、计算执行和结果提取功能。

##  主要特性

- **多软件支持**: Gaussian、CP2K、Quantum ESPRESSO
- **统一配置**: 集中管理原子类型、电荷和自旋多重度
- **力常数计算**: 所有软件包都支持能量和力的计算
- **批量处理**: 自动生成71×71网格的计算点
- **结果提取**: 自动提取能量和力信息，生成CSV格式输出
- **离子态配置**: 支持自定义电荷和自旋多重度

##  项目结构

```
run-big/
├── README_zh.md                 # 中文说明文档
├── README_en.md                 # 英文说明文档
├── atom_config.py               # 统一配置文件
├── generate_gaussian_input.py   # Gaussian输入文件生成器
├── generate_cp2k_input.py       # CP2K输入文件生成器
├── generate_qe_input.py         # QE输入文件生成器
├── read_gaussian.py             # Gaussian结果读取器
├── read_cp2k.py                # CP2K结果读取器
├── read_qe.py                  # QE结果读取器
├── config_reader.py             # 配置读取模块
├── g09.sh                      # Gaussian计算脚本
├── cp2k.sh                     # CP2K计算脚本
├── qe.sh                       # QE计算脚本
└── 其他支持文件...
```

##  配置说明

### 原子配置

在 `atom_config.py` 中配置原子类型：

```python
# 原子配置
ATOM1 = 'H'    # 第一个原子类型
ATOM2 = 'H'    # 第二个原子类型  
ATOM3 = 'Ne'   # 第三个原子类型

# 电荷和自旋多重度配置
CHARGE = 1      # 总电荷 (0 = 中性, 1 = +1, -1 = -1, 等)
MULTIPLICITY = 2  # 自旋多重度 (1 = 单重态, 2 = 双重态, 3 = 三重态, 等)
```

### 预设配置示例

```python
# 有机分子系统
# ATOM1 = 'C'  # 碳原子
# ATOM2 = 'H'  # 氢原子
# ATOM3 = 'O'  # 氧原子
# CHARGE = 0   # 中性分子
# MULTIPLICITY = 1  # 单重态

# 碱金属系统
# ATOM1 = 'Li'  # 锂原子
# ATOM2 = 'Na'  # 钠原子
# ATOM3 = 'K'   # 钾原子
# CHARGE = 1    # +1 电荷
# MULTIPLICITY = 2  # 双重态

# 卤素系统
# ATOM1 = 'F'   # 氟原子
# ATOM2 = 'Cl'  # 氯原子
# ATOM3 = 'Br'  # 溴原子
# CHARGE = -1   # -1 电荷
# MULTIPLICITY = 2  # 双重态
```

## 输出格式

### 统一CSV格式

所有三个软件包都输出相同的CSV格式：

```csv
x,y,z1,z2,z3,z4
0.5,-0.5,-76.123456,0.000000,-0.123456,0.234567
0.55,-0.55,-76.123789,0.000000,-0.123789,0.234890
...
```

**列说明:**
- `x`: 第一个原子坐标
- `y`: 第二个原子坐标  
- `z1`: 总能量 (Hartree)
- `z2`: 第一个原子X方向力 (Hartrees/Bohr)
- `z3`: 第二个原子X方向力 (Hartrees/Bohr)
- `z4`: 第三个原子X方向力 (Hartrees/Bohr)

## 使用方法

### 1. 生成输入文件

```bash
# 生成Gaussian输入
python generate_gaussian_input.py

# 生成CP2K输入  
python generate_cp2k_input.py

# 生成QE输入
python generate_qe_input.py
```

### 2. 运行计算

```bash
# Gaussian
cd H_H_Ne_gaussian_calculations
bash ../g09.sh

# CP2K
cd H_H_Ne_cp2k_calculations  
bash ../cp2k.sh

# QE
cd H_H_Ne_qe_calculations
bash ../qe.sh
```

### 3. 提取结果

```bash
# 提取Gaussian结果
python ../read_gaussian.py

# 提取CP2K结果
python ../read_cp2k.py

# 提取QE结果
python ../read_qe.py
```

## 力计算功能

### Gaussian
- 默认输出力信息，无需额外配置
- 查找模式: "Center Atomic Forces (Hartrees/Bohr)"

### CP2K
- 在输入文件中添加力输出部分：
```fortran
&PRINT
  &FORCES
    &EACH
      GEO_OPT 1
      MD 1
    &END EACH
  &END FORCES
&END PRINT
```

### QE
- 已包含力计算设置：`tprnfor = .true.`
- 查找模式: "Forces acting on atoms (Ry/au):"

## 数据统计

每个read脚本都会显示：

```
数据包含能量和力信息
数据统计:
  总行数: 5041
  总列数: 6
  力信息完整性: 5041/5041 (100.0%)
```

## 注意事项

### 1. 物理合理性
- 确保电荷和自旋多重度与原子类型匹配
- 某些组合可能物理上不合理

### 2. 计算稳定性
- 高自旋多重度可能增加计算难度
- 某些电荷状态可能需要特殊处理

### 3. 基组和赝势
- 修改原子类型后，确保有对应的基组/赝势文件
- 某些原子组合可能需要调整计算参数

## 故障排除

### 常见问题

1. **力信息缺失**
   - 检查输入文件是否包含力计算设置
   - 确认计算成功完成
   - 查看输出文件中的错误信息

2. **格式不匹配**
   - 确保使用最新版本的read脚本
   - 检查输出文件格式是否与预期一致

3. **计算失败**
   - 检查输入参数设置
   - 查看软件的错误日志
   - 验证原子类型和基组设置

### 调试技巧

1. **手动检查输出文件**
   ```bash
   # 查看Gaussian输出
   head -50 H_H_Ne_gaussian_calculations/Ne0.5,H-0.5/Ne0.5,H-0.5.out
   
   # 查看CP2K输出
   head -50 H_H_Ne_cp2k_calculations/Ne0.5,H-0.5/cp2k.out
   
   # 查看QE输出
   head -50 H_H_Ne_qe_calculations/Ne0.5,H-0.5/pw.out
   ```

2. **测试单个文件**
   ```python
   # 测试单个文件的力提取
   from read_gaussian import extract_energy_and_forces_from_gaussian
   energy, f1, f2, f3 = extract_energy_and_forces_from_gaussian("path/to/output.out")
   print(f"能量: {energy}, 力: {f1}, {f2}, {f3}")
   ```

## 功能对比

| 功能 | Gaussian | CP2K | QE |
|------|----------|------|----|
| 能量计算 | ✅ | ✅ | ✅ |
| 力计算 | ✅ | ✅ | ✅ |
| CSV输出 | ✅ | ✅ | ✅ |
| 统一格式 | ✅ | ✅ | ✅ |

## 参考资料

- [Gaussian Manual - Charge and Multiplicity](https://gaussian.com/charge/)
- [CP2K Manual - DFT Settings](https://www.cp2k.org/)
- [Quantum ESPRESSO Manual - System Settings](https://www.quantum-espresso.org/)

## 总结

PES项目现在提供：

✅ **统一输入配置**: 所有软件包都支持离子态和自旋态配置  
✅ **力计算启用**: CP2K和QE现在都计算并输出力信息  
✅ **统一输出格式**: 所有软件包都生成相同格式的CSV文件  
✅ **完整数据提取**: 包含坐标、能量和三个原子的X方向力  

您现在可以使用任意一个软件包来获得完全一致的结果格式！

## 获取帮助

如果遇到问题，请：
1. 检查配置文件语法
2. 验证物理参数的合理性
3. 查看软件的错误日志
4. 联系技术支持或查阅相关文档
