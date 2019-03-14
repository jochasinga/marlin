# A gibberish smali class that stuff in as many syntax
# as possible to test the lexer's completeness.
.class abstract LSandbox;
.super Ljava/lang/Object;
.source "foo.java"
.implements Ljava/io/Closable;

.field static private a:Lio/nokjao/instruments/Fuzz;

.field static public b:Lio/nokjao/instruments/Fum;

.field static protected c:Lio/nokjao/instruments/Fizz;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/util/Set<",
            "Lokhttp3/CertificatePinner$Pin;",
            ">;",
            "Lokhttp3/internal/tls/CertificateChainCleaner;",
            ")V"
        }
    .end annotation
.end field

.annotation system Ldalvik/annotation/Throws;
    value = {
        "(",
        "<;",
        ")V"
    }
.end annotation

.method constructor <init>()V
    # Meh comment
.end method

.method constructor <clinit>()V
    .locals 2
    :try_start
    move v1, v2
    :try_end
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
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/security/cert/CertificateException;
        }
    .end annotation
.end method