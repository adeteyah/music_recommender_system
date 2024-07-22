import time
import sqlite3
import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException

# Load configuration
config = configparser.ConfigParser()
config.read('config.cfg')

SPOTIPY_CLIENT_ID = config['spotify']['client_id']
SPOTIPY_CLIENT_SECRET = config['spotify']['client_secret']
DELAY_TIME = float(config['api']['delay_time'])

user_ids = ["yluff02qnwtul700on69tp1gp", "3yiooz7ohaf5sb5pgfulprebu", "77c9lyw4eerc0ak88emzwwztc", "31w5gibbpyx4h7reoxhmegwpda2q", "og0qa76j35j7t1jggg7jfdr65", "31njh6ntuiy77cf2dh7lyitgo534", "31u43qrzsixceb7prdkwk4ll34bi", "31ngb7u5b76lzzstg7s4vagl23bi", "31sg3vkdzkmiyy4sl2cmvg55fmfa", "z3fd1lm8z7soyexpjc8kljwqs", "j3mdta31m57uvb40esx9s2fw1", "cealqioackf8jwcqe7et71cnm", "3efroa16urbct6yb1y9vu4e62", "31jcr7plpxv5dsrwjfcl33sapmu4", "31apfbweec34fymxn24bkwx3rasa", "31cl3d53eongiedlqdtd6ym6noni", "31imkhp2uuloxfz6cn2emxe2cnia", "31lkuemxalpm5dgupo472sth5znm", "31zshbshpiqn4uz4k5o4ho2cqdra", "313tsoyqwkjmuux2yxvxah6fq2ra", "312i3zlkseufc6km74wncjoaynxq", "31fbbbz45vpfkmubrqpjxi6vxqvu", "31rvoblkmg4ywc5vgm5ygpjmxa7q", "31urcn63lgmglthj2667sbjeisya", "31gqp7h5utpcm6gq7qrn2zyqxa7y", "31new6z6imibvytvgxvxf3qgdr4u", "yye4kc6f4hkd5egc137wr13u4", "s0ky4c703e6cai7k3bul7mk0k", "31swycdnzl3q6gvau2i2uwcvku4y", "31t6yyfhhjwu2h4dqzay3wx3dcry", "31te56samaiu6senpstsa3lfektu", "31eep6ikww6haw7fmygj7ula2bfm", "khc44x429mwf1xqgk4ifu56wu", "31tatuynz3yaubleumhux2grpgom", "31tfj7ukxwh2uvumaetn7p3hgd7q", "31t5vikiatu7cvyaxn366swjct4m", "n8dlb0yl9gfplsd1wppcpu2h6", "315twcasrzhy5b5rnsda2xquhwmu", "31horrjklfvfffu7gh5xsrdwm56q", "31ii3nkmfkde32ivyxfcxz4gkr2u", "5xksalhkm0kdy46aj0v6hv8ty", "31prgg2i67ig7pvndbxtmwc4ftay", "312izlm5cuwqf5jvk5ay5hhbiibu", "0yqfh7h7cratdpgw6slohufou", "3123fukgwqpmrvdwjkw2reumlci4", "31hews4okdwqpp7f5n7pygiz3524", "31gkuqgiau5fc3b7rcqwezhojocm", "dlil61eki8svtxyu28b5xl7l2", "ekvoikmvgw9tipyroql28arfm", "31fxkrmotqxoqhq56lhx7jt7os2q", "kawwns54940sw3az4qij6t3q1", "wc7jd2yt2pcgwozo22g9auc0u", "uvn5zl6zx0fdizszh7t8ne7b3", "31hckvtr43bqpmjtitmcruwpairu", "ee1zcfp1f0naaqa8rkhxnnqzy", "31emd323ajyj4whwymaoan4iwb6i", "cu8f4mx0xj1m84h7ap9n0bkkv", "9blm8w94czy1h18en6isaxgyv", "31ds3praerdvkfbvmrflzdv53mki", "31zhyb7dl2tmawani74rmqd3yk5m", "31cg3t6fwbdzeenc7kp2vlkiacsq", "31zocqtaoxysli7axelrhtn45otm", "31fdo6zruwwkzt5akt52iy5mcfiu", "g2sxbtyy0ukey4faz7rujxv02", "lxar6q2s7lzyu17yb2bbkujq6", "31qymrt6ssjz4qud22jg5ksxug2u", "q238ynw5c218ern00pucg6a5j", "31zeq4pe7g7cxqwocb4iat5v3xwy", "31e6os3yu5kx2txzoonma7q6qsci", "31mpiqgdzf76wcvgvlbu7fj55jxu", "31j4icxe27sn75ynppawidcg4zky", "31i2243mjnu5kvcvrreiuvldo7du", "31mqrbjfo5h4r6dqnzqqe7fl356u", "31yf2fifrgqf3vjwcenyy73yvvxe", "o0oeujwcqwtwmr8rv1kyp22pm", "31m2jsu36ucw54kxwpkxupgy4rbu", "31opmt4jylolc7qhr6ieen5wjzfy", "31p5uklttcilbxusb6uthjqcafo4", "fqxjetjsirphqrydppwcqcaao", "0jl6mpt7kz4734wi6zg10mqoj", "31jzwbenhhanyskvkn34jwulftvu", "31rl76pkwp6yxkac4zvynfeowd34", "4fiaaj60p5wrtxq90aff6eepa", "g7utx93l5a99foqd8cv7hxav9", "31memxmxl6y5henpa3edulmh56eu", "31upwjrfhedpcfb2vw4bfocnhjd4", "6q25zsyrzmto5n75e5k3jg44i", "jt8ed7c7o2handd6ne302lvwa", "31fqtt47iscjwmp6pwaqrcjk3zu4", "314cm2zxmvvzygqgwjxg7izgup4i", "31ratsvs2aukqfxeco2qj7duj5vu", "31m3sm5jnqbmas6kyrk6b2xcc2ey", "31powd47lhzaufdaygjhlhrnblfu", "31m65zv3zvnuhq5d6oo3636z6yfi", "31wzr5lbe2tbtmtpoqmwonoqm23m", "31aldphpjse4myquzbtzwiiysvlu", "31buch2flqfuhsv6jhzz3bkftup4", "7quc8v24qvzkf14qfxw0jpapb", "3153tacmtl4d6dndcroviiksnmr4", "312doeal4exg7ffrtf6aaqfg6t6m", "314vj3wnsjfh3eldvb34iezpxg6a", "31auw2vr4ca6jnt2hhsvg37vznrm", "31kngabmhxxyd5xnulvwqcjlefem", "zsd543o6qtv0r0ndfbou9z8yp", "31ou7vnyomks66r2t6sqh24yntma", "315urll3eb3mjxhomb64z6lxcjbm", "y69rrmpnezifghulidp30drv5", "31agw3jezyh46ja4gxh2tkbvt3a4", "317bo24vrr2nei467nv7iepshyhe", "31p6i3kgmibmrr5g5ok24naev24m", "31cgx46x5ro2joez3rkabfo3eot4", "11154757151", "316ow2o6sf5mhief5xnxiyrmcrtq", "31xkk5ei3jcaxansk4bsevzpifre", "31zcu6xbusykufkqdien36zxlcdq", "1213191842", "316fq2cnprqu43yfrybwfhtmz6zu", "9qicghtoeuyxevurydhgcoh2z", "31vqnchouvqxb6x7yn7ksxh3ge4a", "31z4j6a6soch7jeochcqkcpewgti", "312i5jp6cvhme3gqltehs6mxtloq", "31qwjuyg2tluj5jvvu7fzixe3a2q", "31otnq6m3n3uoxuuxpwwporhizjm", "31wklp5oqry4e6giucvpyg4faxri", "315nzdzml6fckiqrghtreb2tj6my", "gvz0hyba9vykxlsxeo4yw3ang", "yzil9fuiw6ismllcknnzuqnl8", "4zfiivcbn4nxugk5fu3r0sld7", "317ktfkzpafui3mqgv7qx3pgvydi", "31ouqxayqmush477gdanfisbahzq", "2xb9xx6fjk07d4uih56h4nhvt", "31hupd5sqypo4rvb5xzyg2cxneku", "31phxrxupltrczviq7rkljkprm5i", "317k27z74ktpzfifh56sdcpe3j3i", "31lusu76ql6l2ezxwssua2ds3btq", "21llhkmyngr2wjazxgc7ds3ei", "31szhcoxolpfo52tth5y7jgh5dwe", "31wrkqo5sxblv42j5q4lfstws2ye", "f1u3silj0ybgmyaw3a2nkn300", "gepwozmq26uha73r3uxdbrwjq", "31giczpdvn5xqvqsyk5vaa45dnwm", "3166goah4ggx5jhbpetsneb6q4qy", "wlucnx70as0ddo5r3xglqqtlv", "rw3qaxpge0j683vi61bht9tlx", "31vkjrkt5jdwb3myspdnyay45d3a", "31bczvqqlwyasxu2kmxzq3l5t6we", "wioh4jl78yg93h5diaxjjr71l", "31qq5pgn5la3d5lfhgohwtb26gye", "38jsh448axrs58t41jmcqybtp", "31gnahcmmm2vle3z5ajouk4633wi", "31zmpyjcvq44mw2ejusfcwnnbtt4", "317lnnfpypub2fy2zuuhk2zqjuym", "31wtwbbdrjtpnvohepirdut6fesq", "11g1nmjhuxmmua7pybko69fdv", "21dbutcher", "31f4ygeqvi32jxmtmdqw6new75xi", "312autikh6lrnc75nogrjsssdf2m", "p5hbktou7i2jh8ym7ulgs60uj", "31poikhjhrzbweehy6felykw5yde", "b475zcgbt5p800hyt87jqjp8o", "31iontagyng3wq7fwkkqdo5wibh4", "31dwool7kqkgavi4s6ivuhwnojyq", "owr9wpz6h19imxf0x4kxtxdxz", "31u6ym24klwtfg32s4mwy3nxgrei", "ivena", "317qf4qpdmdnmi26gvvpeynwklae", "jfa9nmudrvzho9w7vi24e88lk", "31bufcwidhdwe5ouz2rnqcg2cxhi", "n8e84a1gfl3ggvvnzrmy24q7v", "31bs2xqoutyl6p7tuku7g7sak6qe", "d688wdev0r9238t1qgz0h87c0", "64cr32co4dr7bhjxk01ihmjqk", "0u2i1czckn2o9nh0crytzd4nm", "31hsuobjey3neanqc4l35ywubfmi", "31w44qxkhwtiqk3uewh3f6oshdjy", "31xvvkf6zqepwx5qgol3qz42qpae", "tm6t2qi5qrmg6zx921f7oir63", "31q5sdzww5puwx5a2uhbgvnzgtke", "31qbwtakdmmbrrhiaq6k2yqkedre", "a45dlc4s0qlf89cnalenvm1mu", "galuhm", "4k4nd9thevc8ytu81ksj2hl1r", "31bmuxtcnj7mcpui7ofqlkicocje", "zekrieldimaz", "31f7dowblu65o5tm2ytlihfpmcja", "s65445qip9hcczweryc0yk9rr", "31mv5te6hwhf7zifi3etqg27x4lq", "31kt6icnabnwfydzmfuhittnwum4", "31cmz44vkrascut6umk72753c5pe", "315g67cey7fiizfx3fxi4eb333ua", "31kj7ljb3fxsv7lm2omctz6qsn3a", "31iea2x4wmhs3n6xiufiv37um4ze", "avkk9ljt9tqu66apd0qvhqewi", "38zlwuxmzbsk6kzv1j6wq9sp5", "31vp4cs4u6u34vepj46fqdihdhiq", "lf0kshgvovom8m5ptj6kmv93x", "ajn0zipkwmisezdudqoizsnxt", "31wxvin5xepzehbzjc6sjvttzfom", "3163fv3s7tzwagxnp5zcialif2i4", "ailynnrenteria19", "313zqllec7nfuticfhxp3opahcoa", "31c6rphsdizwlbts24y7b3a7sioe", "31ffynffjhsgu4h422ua7m4wxqbq", "31luugqoq4apmen6zqeortpo47de", "vght0an6cxfe76xf2ixw8mhan", "21uqz3utp7bjlw7botrdamsuy", "31y2kso2m6srmfc7bu6dnkbba2vy", "nrklungmicq03e3zzobwtq14c", "31yd4vmv2vrmkanpm23y66ufjviu", "31kfkvvi4ms3jmybw3r3eis52kdu", "316verfzjcf4gur45uznp3auh4pq", "rzodijl10c4qaaco3vye2h04t", "39vam44v5wkgzengm1wfnfr7g", "wttj8c1latwm9rmwliaqfnbg0", "kzzdh086yxzyigqzvaq23n70g", "31eu2qoeuyxepybcn242md73dawi", "31eslpbtckqytq7cqx77hwycrvt4", "pmgbyv7epr6nn5l4mfvaarytz", "315zdpr3ld2evvtntm3io7xmxxpe", "31mfpjiwvcewi6fppuev56qqsbee", "zbtmic7c0b72u53kzquqn2jgy", "x361ainit7pfi2soasvwtosmc", "31mveny5ofhtrktqgrqwcclomg7a", "qg31f4j0or0xnky4ah12msdcv", "31j7j5qd7vago3etq7ucecnsy4pq", "316mjncwi77q3suwwdanwwagrgie", "314mlvbcjz5xmodpknqpeigfzv2u", "31q44vjdpyskdmbewpw2beel2gnq", "31cedwbocw43eziyfsnoaght7usu", "31v4fqciq5jp7ubyewbsz5xfgwgq", "31b56r43xrq75dygsojhxq7q6j44", "hevus6ftmtyh7b1m7pji1z5w2", "31g44gujkeiggofvepzcgp2ppk3y", "31qbl6zrvw4q2ibokbepvjwbilha", "31csv3uonbrkgj22o4ja233hikjq", "gwpekqnlqh9g1aqbfc4tiivwh", "clwo2eab6m7mzxugpa52h7726", "313ypoeimkjcmyd55c3owcu273fi", "31sjbbtfgiyqo4rvjuizqujdybea", "31fa3vhdf4nugcpxbu7r5lh7flfi", "31rpubnxuqn7kbm33uv4cgqha43q", "tlufgvdr7gqarp2mp1czcjezs", "31malh3gpcdn37d4stxz2nntpd2y", "31e6dikc6hlyihbj36zavohvtj3e", "cdovzng40kfxuev419z57j7uj", "31cpww7lrgjxk355njzykdi5wlq4", "igr4uczkwlm86zrw4g8c2y086", "ojj1m0x9zv071ewzzxpqe4gw9", "31yqnweniuapwg5eqpdtyvrs723y", "31bax4kq4bogdkyghklgdi7qo2bm",
            "31bkmzpi6m27ft46t7grfzj32mde", "31scg5t6spkme6rw2geqyh5x6xyu", "31untxr3ywx5wim3u3nec5f46wza", "4bjy5vi4rxwcr5iqvjgin2e04", "315sr6fdc7atmwxaumi6idxpbq2q", "31f2vairt3rqpd4flpyg2mmjnrxa", "21oom8h17g74093lervs34u2z", "a4uit9x9491bnlm3buar24jts", "49ah36obmqx75x9qaxr3lep29", "31ex3pdpvt7ksehgtsbgcm5k5fme", "31n3t3mfparqfwipshe7myee32xe", "31sj2zujejrhjko6ejblgazbhtt4", "21llwb2xam4hq5zdpnw4pki3y", "31wz447ayc33pch542eqpw3tdbvu", "315adghbr6wpoonar6elnogiqvuy", "tlifgszj6afkawp75rp5a8o9g", "316jxcbk6zv3ycth2efo5uhxeqgy", "xqpt9b4ybkankvos3wi5bpvjq", "31ey7pwluroi2jtsqicezjeh2m34", "31bkzog4mb5fzcy7wywlfvnedwlu", "31cdwcymmj6q4qyfq5e4zgw7eb7u", "onjy7xyitcbqaca4wl4d29x7v", "3122hx45banrxmqxfjjbaaqtmpwi", "31ewuujzszk6oycfvdxmocmkudaq", "x867s31q1bspux3itm15o5qge", "b1cwi5mvl86z4b7p46vmjoq2i", "313uggsz3ibdxweihs2miw4xr5im", "31rnn3xt5kaueu2qalfejkemw3i4", "a16ezxsixs1gnirz3m59bdfgf", "h85vegh962a7bj2yb4pew43hn", "sc34mio3ssd1uvbrfvpi6pkk8", "n4esbp67hk9w5adyj6tl96oqc", "31i7b27dyeqallz3jnj5alwifoda", "31rhtpkkbk5mwelkf6n6oc4fgl3q", "31ww7ycvn2v2efclt2pide4l7sjm", "31xa4elu7cgu3tdcnvnr2mnaec7e", "abqj7afxu7rxkb49rjt20loe9", "31puyjcvq62uiesxxeyxoobmus2m", "3kzfc4iynszhil05q0acjgt4m", "pzl4dsl6c77mo7bt2ow6itbjc", "31af2cgs4rl4dgjdxxruhbwsnaze", "llxdkhw5c7b9i384f9mvig7o0", "0h2brcve4yaz6le5pyolkl5yf", "316awh4dg3fi7gjhxhp4mptp7wqy", "31pnddhti7mpsv6drty5msaypq4a", "445b38m2srygwmtiab287l6ax", "7p7msltsvktcjj5z373yim8p6", "rlcsxp1dfk4kzycunzf0d575x", "31o6gn3nzwlp3kovw2n7czgrmiie", "314373engmw2aoqn42bopuoruzgm", "312ainemt5kkcoo2lm5d7yus4phe", "312tnpnfcfbcplwa6flc6j2vatd4", "31q2qyvidtymrkhmxnkf6cxujbke", "31zo42hg7xwu42hxnazidtbhyu4m", "8ttis36cman9387qv5xg8whjs", "217pnmdkvn4ae7ex5tkcwgkmq", "31um7k6tkdznxazoe2jler45ilpm", "31vyeu5p6zv2t2aevc6hu6okngue", "k2xhhsexhrqo1opm4de73wgt7", "31cgjhzpnmfznbemrefhhvfh2vom", "nazl4", "314co727rwqnr2oommf772faefn4", "31bjg4ujqhdatydzkzohxyee6x3e", "31krnbnpktii3spf3wlcktfwe6c4", "31m3ts3wy4mhx6j52mix5kqftfju", "31exn7zkatydj6gcs2wxyvmnb4ua", "31o5oedf3xs2coxkf2wqcjdzompq", "31cp524xwykmxya54kd3vhkh5v6e", "31fxb2eaqatqc5breur47bjtjbi4", "314h4fmps5ncgx6vx5kuy2736uka", "5yowdwe9i2vgzco68e23n76p3", "keqxpluki70vt4ruktn80x33f", "312tsctxv6bvtm3i4xfak7o3gopa", "31ga5i25baoiweb3pdeedhpmem7a", "31pqeorecxh55iqxvs5puuifrr6m", "31s66wpewjaipkbgkjlkcwkw5j6m", "6rl4oiocv9a5b9ri6zzpu0bib", "046420nh4ftmspbh3fgr26tve", "z255f15mvknq0dpv0dh6chh26", "31mo2oq2j77kz77nqbqueauwalzi", "98e7ozr548cz06e3hlgs31n5l", "31wpsmgpakfdi4y2jkvwlkn5db4y", "3v64lrg03ejhj51hv344wftdh", "31lkqgjjwk6j7szrkygin2jre6tm", "ccd2p250a1geqr8lbvmi78odz", "31coe6wchpsj3fb3ufywtbb33viy", "i9erduboczjg27eclaanc8k2u", "31avwb4cce5o3dbids5oikyvp5x4", "31agz664gvkbxmom7f5277mvhpdu", "31yr4vfrikreohkfwg7hi7xrqafa", "316nyqlo2tcify5oddiqgdkpmx4m", "31yyknecxvo4cntljegyf3dhjw6a", "31zyma3wvbf2u7zaq7t3wkgkfgru", "byeo7xnmbiw4f01kdiyknxy9b", "kmkas4p2o0qxinfvdbc4h6l24", "31573frplchxodsp4hl5jiofyxyu", "im0mc1c5iuej4zndub5jugvve", "drrbqbyyl62anidx85mtjat20", "31v4bv24y4cf6pwb7yygobiaa3da", "31abjcvpt5ejf62hfh43azfmkhaq", "31e4k55sbybzgkq3qxlc5ltesy6i", "4i4ec3lb89mhmje7zsj9yvegs", "31xi5w75h6mxe7uv7iffh45q7pqi", "314kjken5b4qvvsgdvuxichkcwhy", "31ymm2crwfk3icmmeoyw3ulmlxue", "u32s6l3n3vmrlm31eqh888kjt", "21pvvceorsuxvoa3ogn35nvey", "oiimxrye9ue9qa43g7kmef0x0", "86bfhkmosztfevvkahfp56f2o", "31mhpxghjva2pmmtcptgxphvedfe", "8vdpitnwplzig0h1h73r5ids1", "0fjfu2jdhuljjxzp0knkd2mc9", "cwzltmhpo7p1ny35ik8rtkwyw", "xdvy6i4igh8258jvlqv36pumr", "31noyz7bqvmd6d6acguyievqox6i", "ru0aljgcd0ikb4b9bu2n6ozui", "31l6iuudmbpqnkxqsiuj3gowzqmu", "heo7nfg1prqej5t502x050gnw", "3127lrpwep234gec6hg7i47qigmm", "skwb7v0ykos7sawk2jbxhsnsx", "d16ssaarmoy8dy9mkc5r2hu5k", "yrtzg3s30zikduazl20mykvzw", "31zqhhfcf3i7dvpvoijnr7c25kia", "317yczxgshsmqiauradvczkjbnh4", "ebxo0jhtausz1hl77pzppybzl", "97gji086g81f2fs2o5x7jzc36", "9qo2jd888xx6g6oh836xdjbzc", "31bqh3qagg3rlkyagdk4cc4gffvy", "31s7hrgzj7eiwajs3brehorarb4u", "kc4ny34potz83ovru1iyav0wn", "mpio6xbyog0obad2sf0qcoddg", "31ovvn7jii5exit2ogh3dnnk2goy", "i4lrr3kfqr46yyck0jwnmymo7", "31jjz6swcbxm2orakxfabewyci6i", "qo8raoe7fvn67fdhvtsg7rui6", "31h55n5bgydetuad5myd6wvedit4", "31sfhq6lzdqkq4u7klzjm3jjkj5a", "b41r0w6e4p5bmpcrap5ax7e5x", "derickjoshua", "316epl6rw3ro34x3kcypipvs75la", "31zbjzyv6qgpng6yqbq3t7uwbdju", "317qd4ds3nby4nxw27e5qfzm33a4", "31ajm6lbpwo2d6emlazfegswmcli", "31wamtxo54dei5bipdox6ucapnbm", "7dmk731ndpctpe944rla7yixs", "31obxnxwyqouibm4nxpfou53tssa", "317rey6o6ltyrii37lmk5xy4bjwq", "tfrjqtlkcven9cyzob72619a3", "31tcmi6ou7uhstp3oenwy3ktog6e", "31fr5sq2dc57xjsb2qjqxysrlhju", "31opwiuncytczcgixnr5sncbcqn4", "31r5az7gepjzc4obqrzmslebhy6q", "xurrlp5hm769s2t2o2erbccnt", "31mdui4el3aslnmkxvidjbc5rxxq", "31nn7rk2u3duvxru5bwjcvvzgsha", "31h7fyhs2yzuty6dqkwe3mfjuwqi", "31rcb2lmviv6zwijkyhczj25ftpu", "31dxzgxthgrtjvxp3znpgkw7zpnm", "saraha724", "7sqvjtjcj9bvbm7uoxnbkxbtu", "0ciqo4whztzut99t57cbs3web", "6m4l6g28eymbup6dhzk5v3y4f", "31iagopowwf6cjfluhde2uv6ptay", "31s3jiykttdjbkazhzrxit65b6fu", "31a236jzywk7e24d3nkdjcysdxtu", "50sxxzwbxkwptebhtoa6dbxqb", "313mydnnuyhtj4kbqitxuwx57dge", "9okyrnhjj3j0c2gwfx2akf2ew", "zp8yfqga0b006euq3ttwp0qor", "31vgv3jcmmuefreshejd2andwqtq", "31u6zl54z7vyl3vpxrzrwzzrx2su", "31jb7bmwk2o263qr2fy5e6fbdgde", "31ap7vwwfubaert6jnq3oegoyccu", "3144umblkplmnbjolqs3mscztnqy", "31ayyneqiah7itrboat5kunhsrxe", "31qcuo2szpncb5ssupogtb34u6oy", "31gjo62hoo6afrgi3zrbbwtxu7z4", "zmbx7qqx7vtf2jrln434trg3o", "31z36levqjsqb4sh7yznsckantem", "31obslugwiip2dlirietch55gkxm", "dlfjasou86ou820rqwuv48g9j", "317t5zzd37ui7b6xetvg5kvr2wea", "31y7ptlb73mhzdipqub272atyb2a", "31urzog4h4s3zw2q6fb5lhb4z37i", "31tzjomv5wjfkwrbxu6ordznys2e", "31u76iybk4yig3urc7frneljr7ji", "31lmsgdzodkg2kr55cjmutkayvqe", "31mnd4lhkbuam6uhloi6vi2a6ave", "31b24prtvyklukaqjojxjhdvqx34", "313xiastkohw5ezhrddphxdoc2pm", "31tfzirejou3njmljxueyf7ttkqm", "31ngheqqya6delyjqabhivl4x4pa", "x5un65a3nt9wai8o0f35jbyhx", "31wbxdcucqxo4vopr576mpwfunfq", "co77u1wocy1p8k46qh3exdz6h", "d6d3xa8lsvnb4rfxzg2tptaj3", "31e2jkbqqeqon6mfdwrl6wewbrum", "31j3dlfmrrhj45nya3jl6abfphnm", "31y5s6avtxunbnyemiczr5bevhte", "317a2whahl7dj24atatri4m6gs3y", "r3ewjmygfvmj4591kc8wig4bb", "jcuhmxl4qemhb11nu68i0w1rp", "57tkayniih1x33wga8xr5xwlz", "315wlt4xix5gpl52jrii3y6nsula", "31ltwthk27qfacgwldvj7nmmrzxu", "krw1d0e28ywypi6mwnojnauva", "ldxi3uldm5kj0ts7qoeuh243w", "31wrq5nzyv2kneeixhnlosyozoym", "71tfw3plgk8v2x3ftkvxk7768", "cy11d528eiiw0dy6tci1diacf", "31mzhtemzrqnpeb7pydytakiilsm", "31xfzvroruvfimkxkv4zpkge7hgy", "31ayp4zdedwzm6ps5yunibvc5ori", "31bqolldt65u4inewd3j5zvjyppm", "f49j38tn1t99o7hmenm9qxwrw", "9yvdo4s8nwv2zfjx3r43odhei", "31ed6lola6uxl4iwce2fvki67a4u", "31qz7ufmlzyp7gudjaqvxfhul264", "31gcoxw2si5lz3j5ums6skuie3vq", "313hsp5xg3gzcvw3pt24zjqbcpiq", "db44hkhq5kud5dsvgj90j29t1", "anaskachandra", "314fa5jeyzeze2gu2ezllvjn44ii", "nqkth3g0tg7lmr76ow2588de0", "gjr700gi5ds7o0ocjd5ng75dk", "31xcouy2j7pk4rje2pqelfw2weiy", "31tc7xavagz4xprffgmq2d76bc3i", "dok2b9xrivykia74j5x9qylv6", "31xw5djoifgg5vxcnmyiimahcxiu", "kqyfyd7wq1mdjy7323xywf2kj", "316zok6eo6okqpddzyljnrhuf22y", "31syuhksicuw2mlu6wjks325ivs4", "wkgpklizwfwwb1iff3g9809zz", "21pmy5mvms2nbvaa22wnuzkqa", "31qyusyeukndu5dvr455foe2eo24", "6fl6689lzs4md2omkw4kvivs4", "2bls7i37114ertz7599dj055u", "215hm5yqkevlngopmjwky5gpy", "31wsvxsly4keehfinaxgox3qtl7a", "qn26aofe90m6dim4vz28bgbo8", "315pz2xubqwzogcgiew3xax74ug4", "31j2nu3u44kwrpgdirqjapn3jwzu", "znimozwyib0tdjnjcdwufq3o8", "31liuooi3rnoobn46pb6uda7v7ny", "31ccsqff6tsudhnpswetlh2cj7cm", "312hahrcczi3a5j7cae6z7zg6a74", "31fvuws37xpi6vhosbpf2zmsobz4", "98enyo5twrupsyf524lywkusw", "31cxgehazznr7mhobwkobqp3qyo4", "31y6actkuzzxk3acwcbyq2mt54pi"]

client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# SQLite database file paths
playlists_db_path = config['db']['playlists_db']
songs_db_path = config['db']['songs_db']


def create_connection(db_file):
    try:
        return sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None


def fetch_and_store_playlist_data(user_id, conn_playlists, conn_songs):
    try:
        offset = 0
        limit = 1
        fetched_playlist_ids = set()

        while True:
            playlists = sp.user_playlists(user_id, offset=offset, limit=limit)
            if not playlists['items']:
                break

            for playlist in playlists['items']:
                if playlist['public']:
                    playlist_id = playlist['id']
                    if playlist_id in fetched_playlist_ids:
                        continue

                    fetched_playlist_ids.add(playlist_id)

                    playlist_details = sp.playlist(playlist_id)
                    if playlist_details['tracks']['total'] <= 5:
                        print(f"Skipping playlist {
                              playlist_id}, not enough tracks.")
                        continue

                    # Store playlist details
                    cursor = conn_playlists.cursor()
                    cursor.execute('''
                        INSERT OR IGNORE INTO playlists (playlist_id, creator_id, original_track_count)
                        VALUES (?, ?, ?)
                    ''', (playlist_id, user_id, playlist_details['tracks']['total']))
                    conn_playlists.commit()

                    # Store playlist items
                    track_ids = [track['track']['id'] for track in playlist_details['tracks']
                                 ['items'][:24] if track['track']['id'] is not None]
                    if not track_ids:
                        continue

                    playlist_items = ','.join(track_ids)
                    cursor.execute('''
                        INSERT OR REPLACE INTO items (playlist_id, playlist_items)
                        VALUES (?, ?)
                    ''', (playlist_id, playlist_items))
                    conn_playlists.commit()

                    # Fetch and store track and artist details
                    track_data = sp.tracks(track_ids)
                    audio_features_list = sp.audio_features(track_ids)

                    for track, audio_features in zip(track_data['tracks'], audio_features_list):
                        if track is None or audio_features is None:
                            continue

                        track_id = track['id']
                        track_name = track['name']
                        artist_ids = ",".join([artist['id']
                                              for artist in track['artists']])
                        duration_ms = track['duration_ms']
                        popularity = track['popularity']
                        acousticness = audio_features['acousticness']
                        danceability = audio_features['danceability']
                        energy = audio_features['energy']
                        instrumentalness = audio_features['instrumentalness']
                        key = audio_features['key']
                        liveness = audio_features['liveness']
                        loudness = audio_features['loudness']
                        mode = audio_features['mode']
                        speechiness = audio_features['speechiness']
                        tempo = audio_features['tempo']
                        time_signature = audio_features['time_signature']
                        valence = audio_features['valence']

                        # Ensure no data is missing
                        if None in [track_id, track_name, artist_ids, duration_ms, popularity,
                                    acousticness, danceability, energy, instrumentalness, key,
                                    liveness, loudness, mode, speechiness, tempo, time_signature, valence]:
                            print(f"Skipping track {
                                  track_id} due to missing data.")
                            continue

                        # Store track details
                        cursor = conn_songs.cursor()
                        cursor.execute('''
                            INSERT OR IGNORE INTO tracks (track_id, track_name, artist_ids, duration_ms, popularity, 
                            acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, 
                            speechiness, tempo, time_signature, valence) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            track_id, track_name, artist_ids, duration_ms, popularity,
                            acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode,
                            speechiness, tempo, time_signature, valence
                        ))

                        # Store artist details
                        for artist in track['artists']:
                            artist_id = artist['id']
                            artist_info = sp.artist(artist_id)
                            artist_name = artist_info['name']
                            artist_genres = ",".join(artist_info['genres'])

                            if None in [artist_id, artist_name, artist_genres]:
                                print(f"Skipping artist {
                                      artist_id} due to missing data.")
                                continue

                            cursor.execute('''
                                INSERT OR IGNORE INTO artists (artist_id, artist_name, artist_genres) 
                                VALUES (?, ?, ?)
                            ''', (artist_id, artist_name, artist_genres))
                            print(f'Updated artist name, genres for {
                                  artist_id}: {artist_name}, {artist_genres}')

                        conn_songs.commit()

                    print(f"Saved playlist details for {playlist_id}")
                    time.sleep(DELAY_TIME)

            offset += limit

    except SpotifyException as e:
        if e.http_status == 429:
            print(f"Rate limit exceeded for user: {user_id}")
        else:
            print(f"Spotify error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    fetched_users_file = config['file']['fetched_users']
    fetched_users = set()

    try:
        with open(fetched_users_file, 'r') as f:
            fetched_users.update(f.read().splitlines())
    except FileNotFoundError:
        pass

    conn_playlists = create_connection(playlists_db_path)
    conn_songs = create_connection(songs_db_path)

    if conn_playlists is None or conn_songs is None:
        print("Error! Cannot create the database connections.")
        return

    for user_id in user_ids:
        if user_id in fetched_users:
            print(f"Skipping {user_id}, already fetched.")
            continue

        fetch_and_store_playlist_data(user_id, conn_playlists, conn_songs)
        fetched_users.add(user_id)

        # Append user_id to fetched_users_file after processing
        with open(fetched_users_file, 'a') as f:
            f.write(user_id + '\n')

    conn_playlists.close()
    conn_songs.close()

    print("Playlist scraping completed.")


if __name__ == "__main__":
    main()
