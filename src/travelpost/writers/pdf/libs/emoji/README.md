# README

In another folder execute:

```shell
git clone --filter=blob:none --sparse https://github.com/zhdsmy/apple-emoji
git sparse-checkout set png/160
```

and set the `PATH` of this Python-package to the main directory which comprises
the `png/160` directories.
