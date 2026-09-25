# 骨架生成与幂等重生成（从 0 实现）

仓库里只有本说明、`samples/**` 与 `.gitignore`：生成器与测试都从零写，Python 3.13 标准库、无构建无依赖。`samples/defs/**` 是定义，`samples/generated-before/**` 是上次生成的快照，`samples/expected/**` 是期望结果，`samples/notes.md` 是现场记录。

## 一、范围

要做：读一批定义，生成数据类型、客户端存根、服务端骨架；重生成时按标记把手写段落原样搬进新骨架，写出清单与改名记录。不做：网络、跨定义引用、泛型/联合/递归、多语言后端、格式化与文档生成、`.bak` 备份、第三方库、构建步骤。

## 二、口径与公式

**归一化**：对象内键无序，只有 `types`、`operations`、`fields` 按 `name` 的 ASCII 升序重排，`values` 保持书写顺序；缺的键按第四节默认值补齐；字段 `type` 去空格后看待。

**摘要**（12 位十六进制）：`rev = sha256(json.dumps(对象, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8'))[:12]`，数据类型用 `{"types": …}`、客户端与服务端用 `{"types": …, "operations": …}`；`skel = sha256(骨架去掉第一行)[:12]`，骨架见第三节。

**命名**：产物是 `model_<定义名>.py`、`client_<定义名>.py`、`server_<定义名>.py`（定义名的 `-` 写成 `_`）；定义名匹配 `[a-z][a-z0-9_-]*`，记录与枚举名匹配 `[A-Z][A-Za-z0-9_]*` 且不得是 `dataclasses`、`enum`、`typing`、`Any`、`dataclass`、`StrEnum`、`field`，枚举值匹配 `[a-z][a-z0-9_]*` 且同枚举内唯一（成员名大写），操作名匹配 `[A-Z][A-Za-z0-9_]*`（方法名是其下划线小写）；不满足即报错退出。

**改名**：字段名匹配 `[A-Za-z_][A-Za-z0-9_-]*`，先做朴素转换（字段 `-` 写成 `_`、操作名转下划线小写），这步不算改名；朴素名碰关键字（`keyword.kwlist`/`softkwlist`）或内置名（`dir(builtins)`）就加一个 `_`，同记录（操作则同文件）撞名时按**原名 ASCII 升序**先到者先占、后来者加 `_2`、`_3`……。只有「生成名 ≠ 朴素名」的进改名记录，线格式一律用原名：`FIELD_NAMES`（模型，`{记录名: {生成名: 原名}}`）、`OP_NAMES`（客户端与服务端）。

## 三、手写区与重生成

**标记**：起止两行是 `<缩进># >>> stubforge:hand <块名>` 与 `<缩进># <<< stubforge:hand <块名>`，块名匹配 `[a-z][a-z0-9_]*`，标记行是整行、缩进原样保留。**块内容**是两行之间的原始字节，刚生成时为空；**骨架**是删掉所有块内容后的字节。

块名由**原名**转下划线小写：数据类型每记录一个 `<记录名>_rules`（在生成的 `validate` 方法体里），客户端每操作一个 `<操作名>_hooks`、服务端每操作一个 `<操作名>_impl`（都在方法体开头，`raise NotImplementedError` 在其后），服务端末尾加一个 `server_setup`。

**判定**（每文件依次判，结果即清单里的类别）：① 目标不存在 → `新增`（块留空）；② 无 `stubforge` 头、头里 `rev`/`skel` 与实际不符、或块标记不合法（缺止标记、重名、嵌套）→ `更新`；③ 模板里有、现场没有的块 → `更新`；④ 其余 → `原样保留`：不写盘、逐字节不变、`mtime` 不动。

`新增`/`更新` 整文件重写：生成区按定义重写，能对上的块逐字节搬，搬不了的（标记不合法、多出来的块）记 `lost`——**一处不合法就整份文件的块都不搬**；写盘前整批 `compile()`，过不去就中止、退出码 1、不写文件。

## 四、输入输出与文件格式

本节文件都是 UTF-8（无 BOM）、单 `\n`、末行有换行；生成的 `.py` 里由生成器写出的字符只用 ASCII。

**定义 `samples/defs/<名>.json`**：`name` 是定义名、决定输出文件名；类型有 `name`、`kind`（默认 `record`，可写 `enum`）与 `fields`（记录）或 `values`（枚举）；字段有 `name`、`type`、`optional`（默认 `false`）、`default`（只允许标量）。`type` 取 `str`/`int`/`float`/`bool`/`list<T>`/`map<str, T>` 或本定义里的记录/枚举名，可嵌套；`optional: true` 生成 `T | None`（无 `default` 则默认 `None`）。字段名在记录内唯一、操作名唯一，`request`/`response` 必须指向本定义的记录；定义名重复时归一化后相同只算一份（取文件名升序第一份），不同就报错退出。

**三类产物**，首行固定 `# stubforge: kind=<model|client|server> def=<定义名> rev=<12 位> skel=<12 位>`：

- `model_*.py`：枚举是 `enum.StrEnum`（成员按 `values` 顺序）；记录是 `@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)`，字段按名字升序，带 `to_wire()`（键是原名，`None` 也写入）、`from_wire(obj)`（按原名解析，必填缺失或类型不符抛 `ValueError`，`int` 不收 `bool`）、`validate()`（方法体是手写块）。
- `client_*.py`：`<定义名转 Pascal>Client`，`__init__(self, call)` 收 `call(原名, dict)`；每操作一个方法，先手写块，再 `return <响应类型>.from_wire(self._call("<原名>", request.to_wire()))`。
- `server_*.py`：`<定义名转 Pascal>Servicer`，每操作一个方法，先手写块，再 `raise NotImplementedError("<原名>")`；`dispatch(name, payload)` 收**原名**，按 `OP_NAMES` 反查方法并返回响应的 `to_wire()`，找不到就抛 `NotImplementedError`。

**清单与改名记录**：`<输出目录>/manifest.txt` 首行固定 `# 生成清单：每个目标文件一行，按路径 ASCII 升序`，随后每个目标文件一行（路径升序）`FILE|<新增|更新|原样保留>|<文件名>|<rev>|<块名>=<块内容 sha256 前 8 位|->,<块名>=lost`，末行 `TOTAL|新增=a|更新=b|原样保留=c`；块按块名升序，空块 `-`、没搬过来 `lost`，现场多出来的块也写 `<块名>=lost`。`<输出目录>/renames.txt` 首行固定 `# 改名记录：按路径、字段在前、原名 ASCII 升序`，随后每行 `RENAME|<文件名>|<字段|操作>|<原名>|<生成名>`，按路径、`字段` 在前、原名升序。

**命令**：仓库根目录执行 `python stubforge.py gen <定义目录> <输出目录>`；按文件名升序读入所有 `.json`，全部归一化通过才开始写；只写输出目录与 `var/`，诊断走 stderr；退出码 0 表示跑完，1 表示输入或定义不可用且未写文件。

## 五、性能与验收口径

样例 3 份定义／9 个目标文件／19 个类型／54 个字段／6 个操作。测试机（Windows + Python 3.13）：`gen` ≤ 1 秒、第二遍（全 `原样保留`）≤ 0.5 秒；隐藏验收放大到 40 份定义、字段 ≤ 1200、单文件 ≤ 200 KB，要求 ≤ 5 秒、峰值内存 ≤ 64 MiB（`tracemalloc` 扣基线）。

1. 清单与手写区：把 `samples/generated-before/*` 铺进 `out/` 后跑 `python stubforge.py gen samples/defs out`，`out/manifest.txt`、`out/renames.txt` 与 `samples/expected/` 下同名文件逐字节相同；再跑一遍应全变 `原样保留` 且 `.py` 一个字节没动；判 `原样保留` 的文件与快照逐字节相同（`mtime` 不变）。
2. 生成物：`python -m compileall -q out` 通过、模块能导入并各调用一次（记录 `to_wire()`/`from_wire()` 往返相等、`validate()` 一次；客户端注入假通道后每个方法一次；服务端块为空时每个方法抛 `NotImplementedError`，`dispatch("<原名>", payload)` 走到对应方法）。
3. 幂等与确定性：清空输出目录重跑，产物逐字节相同；不依赖系统时钟、随机数、迭代顺序与 `PYTHONHASHSEED`；`out/`、`var/` 不入库。

## 六、样例说明

- `defs/billing.json` / `billing-reordered.json`：嵌套类型（`ChargeCardRequest.amount` 是 `Money`）、可选字段、默认值、`map<str,str>`；后者是同一接口的另一种写法（顺序不同、省掉默认键）→ 归一化后只算一份，三个文件都 `原样保留`。
- `defs/events.json`：`class`/`from` 撞关键字，`id`/`type`/`next` 撞内置名，`card-id` 与 `card_id` 撞成 `card_id`/`card_id_2`，`Import`/`List` 变 `import_`/`list_`。
- `defs/inventory.json`：7 个记录、26 个字段，模型与客户端不在快照里 → `新增`。
- `generated-before/`：`model_billing.py`、`client_billing.py` 夹着手写块 → `原样保留`（一个字节都不许动）；`server_billing.py` 的生成区被人手改过、`model_events.py` 的 `rev` 是旧版、`client_events.py` 没有 `stubforge` 头、`server_inventory.py` 的块连标记一起没了 → 这四份 `更新`（手写内容原样搬过去，缺的块补成空块）。
- `expected/`：`manifest.txt` 9 行（3 `新增`、4 `更新`、2 `原样保留`，`rev` 与块哈希都写死）；`renames.txt` 6 条字段改名 + 4 条操作改名。

## 七、待补的文档

隐藏验收用例不随仓库提供；生成代码的排版与注释自定；跨定义引用、联合与泛型、其它语言后端、旧文件备份与迁移策略没定。
