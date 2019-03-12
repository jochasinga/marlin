.class abstract LFoo;
.super Ljava/lang/Object;
.source "foo.java"
.implements Ljava/io/Closable;

.field static private a:Lio/nokjao/instruments/Fuzz;
.field static public b:Lio/nokjao/instruments/Fum;

.method constructor <init>()V
.end method

.method static bar()V
    # A comment
    :cond_1
    move v1, v2
    move-object v0, p2
    move/from p1, p0
    move-wide/from16 p1
.end method

.method public isBaz(ISZF)Z
.end method