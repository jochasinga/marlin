.class public LHelloWorld;
# note class structure is L<class path="">;
.super Ljava/lang/Object;

# original java file name
.source "example.java"

# these are class instance variables
.field private someString:Ljava/lang/String;

.field public final someInt:I
.field public final someBool:Z
.field public final someCharArray:[C
.field private someStringArray:[Ljava/lang/String;

.method public constructor <init>(ZLjava/lang/String;I)V
  .locals 6
  .parameter "someBool"
  .parameter "someInt"
  .parameter "exampleString"

  # registers y'all
  .registers 10
  return-void
.end method