# Codexion

## English

A C simulation of developers competing for shared equipment. Each developer needs two USB dongles (license keys) to compile, then spends time debugging and refactoring.

Only one developer can use a dongle at a time. A developer who cannot start the next compilation before a deadline burns out, ending the simulation. Adjust the number of developers, task durations, and waiting order to explore resource sharing.

### Build and run

Requires a C compiler, Make, and POSIX threads for concurrent execution.

```sh
make
./codexion 4 2000 100 100 100 3 0 fifo
./codexion 5 2000 100 100 100 3 0 edf
```

Pass eight arguments in this order. All times are in milliseconds.

| Argument | Meaning |
| --- | --- |
| `number_of_coders` | Number of developers |
| `time_to_burnout` | Deadline measured from the last compilation start |
| `time_to_compile` | Compilation duration |
| `time_to_debug` | Debugging duration |
| `time_to_refactor` | Refactoring duration |
| `number_of_compiles_required` | Required compilations per developer; 0 means no count limit |
| `dongle_cooldown` | Delay before a released dongle can be reused |
| `scheduler` | `fifo` for request order, or `edf` for earliest deadline |

Each log line contains elapsed time, developer number, and action. For example, `0 1 is compiling` means developer 1 starts compiling at the beginning. Execution ends on burnout or when everyone completes the required count.

### Implementation

- Each developer runs in a thread; mutexes protect dongles, shared state, and logs.
- Condition variables and a heap queue manage waiting developers.
- Dongles are acquired in increasing ID order to avoid circular waits.

### Tests

```sh
make test
```

Checks FIFO and EDF completion, burnout with one developer, invalid arguments, and log formatting. Each execution has a timeout.

## 日本語

複数の開発者が共有の機器を取り合いながら作業する様子を再現する、Cのプログラムです。各開発者はコンパイルに2個のUSBドングル（利用許可用のキー）を必要とし、作業後はデバッグとリファクタリングを行います。

同じドングルを同時に使えるのは1人です。次のコンパイルを始められないまま期限を過ぎると、その開発者はバーンアウトして終了します。人数・作業時間・待ち順の決め方を変え、共有資源の待ち合わせを確認できます。

### ビルドと実行

Cコンパイラ・Make・POSIX threads（複数の処理を同時に動かすためのライブラリ）が必要です。

```sh
make
./codexion 4 2000 100 100 100 3 0 fifo
./codexion 5 2000 100 100 100 3 0 edf
```

引数は次の8個を、この順で指定します。時間の単位はミリ秒です。

| 引数 | 内容 |
| --- | --- |
| `number_of_coders` | コーダーの人数 |
| `time_to_burnout` | 最後のコンパイル開始からバーンアウトまでの時間 |
| `time_to_compile` | コンパイルにかかる時間 |
| `time_to_debug` | デバッグにかかる時間 |
| `time_to_refactor` | リファクタリングにかかる時間 |
| `number_of_compiles_required` | 全員が完了すべきコンパイル回数（0で回数制限なし） |
| `dongle_cooldown` | 解放後のドングルを再利用するまでの時間 |
| `scheduler` | `fifo`（要求順）または `edf`（期限が近い順） |

1行のログには、開始からの経過時間・コーダーの番号・動作を出力します。例えば `0 1 is compiling` は、コーダー1が開始直後にコンパイルを始めたことを表します。誰かがバーンアウトするか、全員が指定回数のコンパイルを終えると終了します。

### 実装メモ

- 各コーダーをスレッドとして動かし、ドングル・共有状態・ログをミューテックスで保護します。
- ドングルの待機には条件変数とヒープキューを使い、取得順を調整します。
- 2つのドングルを番号の小さい順に取得し、循環待ちを防ぎます。

### テスト

```sh
make test
```

FIFO・EDFの完了条件、1人の場合のバーンアウト、無効な引数、ログ形式を確認します。各実行にはタイムアウトを設けています。
