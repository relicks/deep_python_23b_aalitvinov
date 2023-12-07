# Домашнее задание #11 (Расширения на C)

## Performance measurements results

```text
Testing 'loads' method...


Testing stdlib json 'loads' performance:
================================
169 ms ± 38.3 ms per loop (mean ± std. dev. of 5 runs, 10 loops each)
best time 140 ms

Testing ujson 'loads' performance:
==========================
143 ms ± 8.2 ms per loop (mean ± std. dev. of 5 runs, 10 loops each)
best time 131 ms
0.85 of stdlib json time

Testing my very own cjson parser 'loads' performance 😢:
=========================================
982 ms ± 41.3 ms per loop (mean ± std. dev. of 5 runs, 10 loops each)
best time 941 ms
5.81 of stdlib json time
6.87 of ujson time

 >>------------------------------------------------<<

Testing 'dumps' method...


Testing stdlib json 'dumps' performance:
================================
188 ms ± 3.0 ms per loop (mean ± std. dev. of 5 runs, 10 loops each)
best time 183 ms

Testing ujson 'dumps' performance:
==========================
98 ms ± 6.2 ms per loop (mean ± std. dev. of 5 runs, 10 loops each)
best time 93 ms
0.52 of stdlib json time

Testing my very own cjson parser 'dumps' performance 😢:
=========================================
674 ms ± 20.8 ms per loop (mean ± std. dev. of 5 runs, 10 loops each)
best time 650 ms
3.59 of stdlib json time
6.88 of ujson time
```
