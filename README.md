# Cursor-pro

突破claude-3.7的限制。（注意把自己的提示词先备份好）

## 功能

* 删除 `globalStorage/state.vscdb` 和 `globalStorage/state.vscdb.backup` 文件
* 清空 `History` 文件夹内的所有内容
* 删除 `workspaceStorage` 文件夹及其内容

## 使用方法


### 使用打包后的exe文件

1. 右键点击打包后的exe文件，选择"以管理员身份运行"

## 配置文件

脚本会自动创建 `config.env` 配置文件，您可以根据需要修改其中的路径设置：

```ini
[PATHS]
# Cursor用户数据目录路径
base_path = C:\Users\用户名\AppData\Roaming\Cursor\User
```
exe文件会在dist文件夹中，配置文件需要和exe放在同一目录。 