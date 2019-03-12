# marlin

Fishing in Smali? try Marlin.

## Problems

[Smali][smali] is a DSL designed to be a readable and editable representation of the [Dalvik Executable (DEX)][dex] known in Android reverse-engineering community for analyses and localization. The common steps are:

1. Obtain an APK file
2. Use [smali assembler][smali] to transform DEX file to Smali.
3. Inspect, modify, and hack the Smali files.
4. Use [baksmali][baksmali] to deassemble Smalis back to DEX.
5. Quite commonly, [apktool][apktool] is used to decode the APK to a structured Smali directory and to build it back to a working APK.

Smali is great for manually inspecting, analyzing, and modifying apps. However, it is tedious to programmatically do so. At my work I needed an interactive environment in which I can experiment with Smali. I also needed a seamless integration with the Python codebase.

## Enters Marlin

Apart from being a really cool fish, Marlin is also a Smali parser / VM that maps to Python. It basically lets you analyze and write Smali code in Python.

Marlin loosely consists of two parts:

## Smali parser & interpreter

Marlin API is in Python. It also has a Python back end. It allows user to interactively parse Smali and emit Python representation so you can write and modify Smali code in Python.

For instance, the following fictitious Smali `Adder.smali` which contains an `Adder` class with a static method `add` that returns the sum of two integers.

```smali
.class public LAdder;
.super Ljava/lang/Object;
.source "adder.java"

.method static public add(II)I
  .locals 1
  add-int v0, p1, p0
  return v0
.end method
```

Without getting into too much detail, it maps roughly to the following Java class:

```java
class Adder {
    static int add(a int, b int) {
        return a + b;
    }
}
```

You can use [baksmali][baksmali] to deassemble the smali and use tool like [jadx][jadx] to convert to Java.

Marlin can parse and emit the following Python equivalence:

```python
class Adder(java.lang.Object):
    @staticmethod
    def add(a, b):
        return a + b
```

## Stack-based VM

Marlin's VM layer provides virtual memory model for all the registers in smali code.

[smali]: https://github.com/JesusFreke/smali/wiki
[dex]: https://source.android.com/devices/tech/dalvik/dex-format.html
[smali]: https://github.com/JesusFreke/smali
[baksmali]: https://github.com/JesusFreke/smali
[apktool]: https://ibotpeaches.github.io/Apktool/
[headspin]: https://headspin.io
[jadx]: https://github.com/skylot/jadx