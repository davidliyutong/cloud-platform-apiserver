# Useful Tips

## How can I get Microsoft's cpptools extension to work with this project?

The cpptools extension is a great tool for C++ development in VSCode. However, it is not provided in VSCode OSS. You can download it from the [Official Repo](https://github.com/microsoft/vscode-cpptools/releases) or use the provided script

```shell
curl -sSL https://gist.github.com/davidliyutong/dad5e8de58ad86d2e0b7ec92ffb79ae7/raw/072f76610c1b3f1080a4024b43344fd62fe84e1b/download-cpptools.sh | bash
```
The script will download the latest version of cpptools and save it to `~/Downloads/cpp-tools.vsix`. You can then install it via UI.

## OOM Kill When Installing `torch`

Instead of installing `torch` via `pip` directly, you should add `--no-cache-dir` to the command. 

```shell
pip --no-cache-dir install torch
```

See [this issue](https://github.com/pytorch/pytorch/issues/1022) for more details: