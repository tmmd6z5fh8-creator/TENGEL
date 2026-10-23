"""brotli の代わり（Python の brotli モジュールが入れられない環境用）：node の zlib（brotli 入り）を使う。
   fontTools が WOFF2 を書くとき（build_fonts.py）だけに使う。使い方：
     try:
         import brotli
     except ImportError:
         import brotli_node as brotli; sys.modules['brotli'] = brotli
   出てくる WOFF2 は brotli の圧縮の結果が少しちがうだけで、フォントの中身（字の形）は同じ。"""
import subprocess

MODE_GENERIC, MODE_TEXT, MODE_FONT = 0, 1, 2
_JS = ("const z=require('zlib');const bufs=[];process.stdin.on('data',d=>bufs.push(d));process.stdin.on('end',()=>{const b=Buffer.concat(bufs);"
       "const mode=+process.argv[1],q=+process.argv[2];const out=process.argv[3]==='d'?z.brotliDecompressSync(b):z.brotliCompressSync(b,{params:{[z.constants.BROTLI_PARAM_QUALITY]:q,"
       "[z.constants.BROTLI_PARAM_MODE]:mode,[z.constants.BROTLI_PARAM_SIZE_HINT]:b.length}});process.stdout.write(out);});")


class error(Exception):
    pass


def _run(data, mode, quality, op):
    r = subprocess.run(['node', '-e', _JS, str(mode), str(quality), op], input=bytes(data), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        raise error(r.stderr.decode('utf-8', 'replace')[:300])
    return r.stdout


def compress(data, mode=MODE_GENERIC, quality=11, lgwin=22, lgblock=0):
    return _run(data, mode, quality, 'c')


def decompress(data):
    return _run(data, 0, 11, 'd')
