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

user_ids = ["31rhdyu32fcpgfnfxpzst5t7yoau", "31mdui4el3aslnmkxvidjbc5rxxq", "m17k60er8grixkf30u691szl3", "31c2xv5ykq4tje3dlc442wmotkqy", "313loe7qwwpthv6dmblkvbsyqdim", "b2ljppxc8vbej8n3mzm5bmotu", "31iwfhbcvmvuleicpagoeck642ri", "31dypk43s7kzsw5gbhtnyjnah36e", "315twcasrzhy5b5rnsda2xquhwmu", "31vtyj6ilzejch5a62jqdm6h7rji", "dv31odhha7zilp8zswz6b4uep", "31ohxff2uxjpfl4wihwxjjerhxb4", "31zkl3bkveznpeqcn2umd4ibdzhm", "31fxkrmotqxoqhq56lhx7jt7os2q", "14lh26ox32pz1g9bkria26bvj", "31r5x5l52wbems746gjk3trlbj3q", "31zui2ffdfc5z5ztx4exloumdz3y", "31nzu4ffq62xf2jkoa6pp3tu6uwe", "xuv4fed3nx85yo7bptfa87c8f", "31e7gtcppmfwgub72qcnzuhtuuqi", "31cvwzlt5q6k3tko73mrtyzqcmga", "31e5vcs4clszlr3buoveahzishfm", "31g2i3fhud4u56hcwcgv3fgym5lq", "31gmkgm5n7hawj3ivqta5nmpafeq", "31unwzmelffqfbrajvuiyk7lkjeu", "31gdaolhitwaes73vadcjodma5jm", "31yd4vmv2vrmkanpm23y66ufjviu", "vontg4rrmyrmzp5f59zou6cnq", "x4hnjxx2cjtli2bkemr9qfhax", "31cdtm7zvl24qnkozlizry4u4b2q", "31pp7nq5tezk2jxjb2iojyxfneny", "31cp524xwykmxya54kd3vhkh5v6e", "313qmv3s7nrmjwesnxm4o6yltx4y", "kuqrwhkrov0jctkvr4ntzktke", "31z3rvwckbs6xt3srd5zw5tpiave", "31t6yyfhhjwu2h4dqzay3wx3dcry", "31wglftx2snlrabr4wnlozn3a6ce", "31muovzigmyep66wm4nueqcj4bzu", "31uft4f2chuua632o4k2ecrjum4m", "16hpkdqpao5uwrpetb160f3bv", "317kxsy3xbdasfeljv7li56io76e", "314upenrcql4imkztgk3tff7zk2y", "31kn76hitfgzqnjigithryxrtqbe", "p29vyr65alnsz5oa3bglkerlt", "nipacj20xy6sqqd29b5tc3vxk", "qsiy8h8syggdgd2b8iv2m3uts", "31bczvqqlwyasxu2kmxzq3l5t6we", "yrmiflfuwzayh1grscfmv84ia", "31o6gn3nzwlp3kovw2n7czgrmiie", "31d5sj5wh7hfy5gsw2ysnb4onirq", "cu4kf76fw6czeaqh7kk7xp507", "31xcm4m5gzkqroixhs3iyajfu77a", "ivfzb45rfbjxyoc18am3p3cdf", "1xwoe5qyzd8pc5ki5fjg93lvn", "cy11d528eiiw0dy6tci1diacf", "312z3e7mj7p7tjw7bwkawz4te6dq", "31cjxxmuzw56rqvd4f34rzd3xi64", "31px4ervdpeyekvridefj6bu7cjm", "h3j6cmwilw2wfi4zqcbkyks2u", "k60cs8u1psmc167qd7znm64tk", "smbyeelc1qooj8wd7m5ts35wy", "312tnpnfcfbcplwa6flc6j2vatd4", "ujgsv4avs0dsq6eh6g486j9jo", "315ppt6hzejphaj7wmrjbrtvkbxe", "31q3hwi4eybq5bfaprt2s64hyjje", "31fdyutkgekxvzghd3zlskpkjh3m", "31dzbmz7qjnea3ebvee6ww6ezqo4", "31lffhvftay2ud23felimxbjcfri", "31uijvygql3vqqucfuld2autf66m", "31n7wfakspbxngazhshrqzojtvyu", "fj9dpi5imk26jbhe7339kfmns", "316m77u5b2a4pk2xi6rqlkvgn3t4", "31oxgb36mctnkikkk677dwpqpqza", "31pxdisrbgoczmugw5mcqpmbvwqe", "31xcinadgppeixl2mmq2qwtxdqsy", "31ayyneqiah7itrboat5kunhsrxe", "31j4icxe27sn75ynppawidcg4zky", "31tonjdvca6azarejylugeoufmxm", "1kx34l7x0zrhusocouugiw1i8", "312zhsbfqmazltsifjhlbukypaki", "31aod36bqoojsx2u3khl5vylrdjy", "31fwg6xqjh7apfo3golgtq4gvb4a", "31enp73lcjynzm4ediodfrzzylee", "31tmd5opqyktdjo3nvupgulp3scm", "31hbhhc75j2xxx7bk5ceom4azdmq", "31iggmvzctzmoqrtlj75hnbilquq", "wrx4wl2aal8s384yk2452qkj0", "31s3txv4plyfgoz6kavmbtn2po4y", "31hq4zk2wmd7db7e6xwqkmu64aie", "mima4jeg4ktxoarl5to0fynkr", "31ksyam5uqvksttjnb47ynplcqou", "31d7u5fzqvorcky7ta2a67ivvywa", "92v567ug642bx5l82xp7fk1re", "31ppaw5easrkwx5rjvtepfib7l7y", "316idi7jng5e6qkhw3h4pvabddke", "3v5pfrewev99uw2cw6nrmp171", "31oiyjggeohmz4y66liuarr4nzde", "3147xhyrmj6utnsn4aqrjv4qjsle", "313mccy3ncc4kafs7i4xnriukqmy", "31usrrekfgbh35ubv2eherpviixy", "wttj8c1latwm9rmwliaqfnbg0", "31qf4q2kvquonglf5lh5nsclr2iu", "acx25wofd8xn0742vv5wz8dln", "ldyu1feykh4irg295ulydr0jc", "315adghbr6wpoonar6elnogiqvuy", "31echrpvcemdvmdcshgudrhx5vm4", "2k6r9ho9prz56zzhmde96wmf0", "31mxtcrp64anqbrirpctz37trjoa", "3pjek5924g25pq7i78fxcu71g", "31mnkg6yv2nkqbjgzhvlujuarboe", "0h2brcve4yaz6le5pyolkl5yf", "jt8ed7c7o2handd6ne302lvwa", "31yo6ohsxqipeohrwamw3pkgu3la", "lpxn9d5iwg4pbhq8k2ihm2nmu", "m1r2h16g17jdftesi2ned988q", "31p6i3kgmibmrr5g5ok24naev24m", "31tjoxe76t6rjn4h4t7sje4r3tya", "sausanbawazir", "31p5uklttcilbxusb6uthjqcafo4", "31hmbz2fp5yllxeoladvl5o4ku2y", "31rl2im2lkjydgsj6jewqvc6pxse", "312zhjx2lgm46tjmciuclm6etway", "y1ps0mnd95mtzwydj0epgh5i4", "31obslugwiip2dlirietch55gkxm", "314o2ervp3xrxs5bw77wcnomg3eu", "31beoyjvzqe3niie7mi37lctszvu", "5buk2jo751xsbo6m4lfpffa79", "31i4yxjgkab3t6rvnj4jbvyw5uvq", "312wfyt37qrrkf6ictx2g4r6k6xy", "e39ooyk86712qwonvpt1hioeg", "p9kp5uuovonsk6vu7qovef246", "31pp6i5wxctzagljza7reb2mits4", "jx1l2l9qf8tuh12qifjgixjjz", "31symu2nioxazgyxyoabccna4x7i", "31zwl5narv4msfcvjzlgtv7e565e", "skwb7v0ykos7sawk2jbxhsnsx", "2o9f66yea8a3c2xorbw115uhk", "3163d4ibi3eqhacbivvrvdy5dlci", "31eu2qoeuyxepybcn242md73dawi", "317qf4qpdmdnmi26gvvpeynwklae", "maoi70ghyr5gbk6grxw171ax8", "31rnn3xt5kaueu2qalfejkemw3i4", "31mbup7xkst5mckbm67fkzkex52y", "31e5dilb575ybn3xzh2ny4jcs77y", "31iekekwpd5dmpyqkzo22gblg7pi", "31allkfgo7h5obuz3vvbm35nbdf4", "t13ensa7dk6y2v4fs5wy3tmgn", "31cy7extfb23ecxb4g3pullzrlea", "31dwojcjgwcvxunh5dmaj2eyrwpm", "31oklahay5xvu7p3ucz7hez7q7w4", "31v4bv24y4cf6pwb7yygobiaa3da", "dinanari", "31rtggayns5bzmmztqbqe2lx5y5e", "31f367qafq2avqk3lgoqgswhxesa", "b81z7jno1at2h3hujkzizmdrt", "fakgpjsmosqbmnr81kutz99i3", "wb16nbmw51fu975ez21vtn0n9", "tzyv1t8c6h97v3q5ntariciah", "31iea2x4wmhs3n6xiufiv37um4ze", "31oxwxzfubwtz6kccd35z4bodxeu", "31osjk4uuk2b6i7ty6imgcquzegq", "31rbewrt7efeb4qqx6opeuugrpcy", "31foxqbaatxzkt7pksd5tdunphim", "13xrrza3fw8k5j2terdqc0ou3", "315g67cey7fiizfx3fxi4eb333ua", "31hksdtg4yqtekwdawqqm5bmzrnq", "31ef4acvrdmg2atr2usl6dwtcfq4", "31oqi2dawbxr73ydk4qdzxwmcaqi", "31ksspesewu5ezrnc54szjwktu3y", "wkgpklizwfwwb1iff3g9809zz", "im0mc1c5iuej4zndub5jugvve", "31uonchrsjvrzeo2faof2lxzcgim", "317hscv5fletl5zsyeggpbkpgfsm", "315e2l6dppaj4om7ysun3osr473i", "31nb4czeqiklk7b7gw6p4apw7jpi", "31iwziwqjhp3b2koptcc6zumfck4", "31ge6467rxo6oibfnu6cb3yi7vvy", "31ujggpcykeflgrv6i5wwnhk2sci", "31qcuo2szpncb5ssupogtb34u6oy", "31olebkhujpbtg5xmizaa2clkyou", "31idcvk3sf2qsjtpx6mbrlv6gsoq", "31sukxdln4xkptcn2khg3hjdupxu", "317rsotraqodp7erxc5o6ryusrzy", "31rtsclabiweapz2spiqnlxe7ham", "31mnd4lhkbuam6uhloi6vi2a6ave", "vxuujs5h01cmizqtkhqeqi4dg", "t1looi81ehdm5pv4cf51w8lzc", "31hzix5rykijvmfz5ait2vjjdcye", "315565s3cobyuqzf7yv2jxgcxbyy", "gvz0hyba9vykxlsxeo4yw3ang", "313b5izukwew4lm2qilryym7vwvu", "gurxzh05nwmzehrs9m6xqiaru", "1hz8vp31h3hncyd5tuafs8v2p", "wncaxmbwrykqq5pxqmga4ldfh", "31w3tbfww54n4o3a5zms4gethh2a", "316nyqlo2tcify5oddiqgdkpmx4m", "317njgu4w3dn6ca75e6us6m46yee", "31wzvpf7kr2wgncb5tiaz7e22fei", "gi6fc39qv2zsfbgm1w7xkieb2", "31a2b7hoayjunozzcv3aqg2eerx4", "31tll2iyjeowucxf2m4qcajnnh34", "ou4qmx06pg89yvrft014q0hwj", "7lpgt7ox415f5cimzlpnio23e", "5thalr14j490nlk8kjaridu1h", "vwhdfareccwjtn98wb67fk3de", "31j3dlfmrrhj45nya3jl6abfphnm", "3175pktg2txgniasz3gx5c6tsufy", "tfrjqtlkcven9cyzob72619a3", "31puyycjkg5xenssgefh2xyi6lli", "31axd6px27nrhv7ztjvseoreuxwu", "31fyublnu4cmibraewf3vffafdha", "2yqpozbxo6awn6bl5quee9j5z", "heapr3vrk1w4oo0bvddsdsio8", "zmeaa9mk2aunsunvtrkhn202l", "uhx3sl6fqgrgtr62stywqsxyj", "315wlt4xix5gpl52jrii3y6nsula", "bfpi669bi2xp58xfql6rqpp4u", "31powd47lhzaufdaygjhlhrnblfu", "31qyusyeukndu5dvr455foe2eo24", "3134qooohm4yghwgbfqrbynl2rde", "31mem5ry7l7s7gch2wrkgeyv7jpa", "31u6zl54z7vyl3vpxrzrwzzrx2su", "rkpozlg09l4b2b1v664kf0mqe", "31h6yvlsconj7ddj3yrjjxydp7ba", "rk2h1bi8yuhkg0n6proaobqkb", "31gsgp32blm55uqa7rskjd4frzx4", "n8dlb0yl9gfplsd1wppcpu2h6", "0yqfh7h7cratdpgw6slohufou", "31eep6ikww6haw7fmygj7ula2bfm", "31gb4dzcp75qhwuleizbsyw5rp7e", "qckheaowan0ou4afuc94nfx1g", "31h5f3g3525wktpr3klrlz7okeiu", "dtur88yby10qri7544ui93aak", "vy54g0xyuu7r5x9wjw154zorr", "uvn5zl6zx0fdizszh7t8ne7b3", "utquzmewof4gzr4qitc4r4acn", "3147ztqshi5j33kijyrhkvmzh3ki", "31xx2tx2kylpartkzduvijkkio5a", "7pzy25m43fb4dbemxttlljuql", "3127lrpwep234gec6hg7i47qigmm", "0adxiugbdudcgcf9n8kw62u0h", "pzits36wic4w25tllrm0wbafd", "31ke45sv7lg3sn4oc7pslblkuhru", "31zrjrrggjwjkskh6adqioshxegy", "316uadraywmipsjft6tzmcpmwuhe", "31tyblqirmbimqugny4pvp5paumm", "jgxxmpb2bf0nqfniouw2jv83r", "31ap7vwwfubaert6jnq3oegoyccu", "31bbmfouz5ah5g47zokzuzurdsvu",
            "31ra2xn3jaw6sx5o2bvrx4bhpb2y", "31u2b6tndzx2vm3bvit46wdjotki", "derickjoshua", "31s3jiykttdjbkazhzrxit65b6fu", "ms3youp3tehyq0h8uctvkj1di", "354m32dty46av1kj5xqboi771", "31rqmtepujqlp3a2v27f6wcyur4q", "31rwyt53mzjnxuvmpkmt2ubeead4", "31hbthfazx55fumxs6eana3s4bqy", "5xksalhkm0kdy46aj0v6hv8ty", "31fdtyyg5gjj5thd52xp4uezuuim", "215x5ibybrjbrsq6dnihkaxci", "31nnlrvwcatq2yclnjwvo4wvktdq", "316dkglnk425h2oiyrp7k3ody77e", "31quzdxd6es3gb4licewp5cr3unm", "31x7avoiu2gketh6fo7bdlio4dfi", "31mmf6ap6r4vy376zzojbvfqxf5q", "31x6bmxvtbp4mqt44n64tcjnubva", "y18yq74p3ecbdrkv9v0vvj940", "317qd4ds3nby4nxw27e5qfzm33a4", "31tfj7ukxwh2uvumaetn7p3hgd7q", "ojj1m0x9zv071ewzzxpqe4gw9", "31z4fb35wl3toewiwgwtzdh3i7v4", "31aldphpjse4myquzbtzwiiysvlu", "31b7hl3y5dlsc7fgbxkjdsab3tn4", "31kngabmhxxyd5xnulvwqcjlefem", "heo7nfg1prqej5t502x050gnw", "og0qa76j35j7t1jggg7jfdr65", "312ainemt5kkcoo2lm5d7yus4phe", "31skygljx4rsnsw3f3ht7sghakdq", "cdovzng40kfxuev419z57j7uj", "31xi5w75h6mxe7uv7iffh45q7pqi", "31qvg3nx4ykrgjje3cvl4rimcilm", "98e7ozr548cz06e3hlgs31n5l", "sanik007", "a395erh3qd0hit6yv7txltsy1", "i9erduboczjg27eclaanc8k2u", "31skrj2qtvplnjfc54qycag72cia", "cealqioackf8jwcqe7et71cnm", "31hdsx2vwojbxtsltyul4d2fgw4e", "31n6i6ajjq3uw6ftunsoyybi3si4", "suplyuf5lt64bv8uqpy5q8spb", "31fvuws37xpi6vhosbpf2zmsobz4", "31x2wknipl53b6nipp2pk3k7kedm", "31isxjjaab7yvwligqbjua2bszdq", "31vyeu5p6zv2t2aevc6hu6okngue", "31rrqbunchlc2imrkknw22ufbz7q", "31q2qyvidtymrkhmxnkf6cxujbke", "llxdkhw5c7b9i384f9mvig7o0", "ap4hioyuckudoh7k11urkfl4y", "4kd6zk1nq6vklfitjif340jtg", "n4esbp67hk9w5adyj6tl96oqc", "31o74ygtfg5nk7rjwornzbjf2pa4", "31qlbobbv64srdkuzymnyfctmupa", "ybouqmyr91lr0j76ld0byu1yf", "31vrmv6nwlgkpcv5o7vleesvfchi", "57tkayniih1x33wga8xr5xwlz", "31hoipusgiz43hjiy3cv62scfbq4", "31my2lugvuqhadteiniptmg3tu5q", "31ekzhwhkc354qhnle72qybdldfi", "31pdhigrrk5t7sdl66eubgeszotu", "diqmek2k8pd85cy2vtezmtl3y", "31qpm2zyqubrmadw4pscjlgdcct4", "udydakfspmuhr5yjoe7d4kh2x", "31cl2grs67pb5xaept5hkn24xblm", "sqiaat3krtyv8cqk1ywa4z5b5", "21v3bqtbwhcbvanwrevrtk3tq", "31huhphubsutf35ijbiw4n6jmdn4", "31f2kaonuqawi5jf3hlr72pqq43m", "31ii3nkmfkde32ivyxfcxz4gkr2u", "31v6qw7sxtvej7nwaotzovtxhqdi", "h8h4kn5g8c192qydsxupkxx7x", "31bufcwidhdwe5ouz2rnqcg2cxhi", "31nstnexbv7ym5yaqswfh2akxixi", "zeopnw8lrenk2ivw08b8747e0", "31f4lypxyqjaiig5ca3p3au3oxrm", "etjd8apuacgtvw4afdmh7z792", "3146oo3tla3ogoro5cvsxipodg24", "31l7lgcg65qy5w5cectouactmyf4", "31fwcghr7lzokcuna6s7js3m7dom", "316svpby33scnjhgpavpiiqglpxm", "31nk5cjv5pom6j5qumxkoxxnxx7y", "31ne67hox3mckd26wo5kvcyptzje", "kc4ny34potz83ovru1iyav0wn", "31bjg4ujqhdatydzkzohxyee6x3e", "31mfxs77xqovxm2vhqgd3ttpxr24", "31zyqvckn5sxvwvcwv546bxgqs4e", "srluvymjplbpkrg1a17wsy9dn", "31wn3adyeqrxlowq5sphzi2znv3y", "31uvefw3v2rpjbvdd3yddthkvlma", "31llyvqphwnabmozbtz4izphygqm", "31k54pkgikmhu7ajbmkx2dp5zxpu", "ty4bt0vwut6s6ksjf0tsp8t6m", "31mzhtemzrqnpeb7pydytakiilsm", "uhcxuymhrqgpb7ssntxq1vn2l", "31647ncttaoso4kqsz6aoidyqatm", "3164zxdtgthqmtpamcd6endbhzn4", "31r7e5c7cgzmznahxmvbre3iddjq", "br8dtaspjuo020l8e2v2v0ibi", "31ovvn7jii5exit2ogh3dnnk2goy", "3152qv5n2xzrya4trjnr5bv7mcsi", "ccrscsjrhnpufdpiwfbk9jfgc", "31gvg3ucujf4ol462uc6e4bg2sxq", "p4so735x25w2rm967psjjrdcq", "31ngb7u5b76lzzstg7s4vagl23bi", "31nhq4wd3epgw6vpfeb5ewk2ekmq", "31f3nfirfv2gxumoyk65qnhayl4y", "4mraq2xb0jbz7b0trfgzpvh8m", "e3bzm2ijo81g3lxz035vesbad", "31fthnoaskjxf5z6ylsxpjbhlw3i", "9mby3xm5bygkmulihqisforuc", "hgr2wxqfc190gvsembnguvpfd", "31yp5i45q7ibfsjslp76dw4lfeu4", "ailynnrenteria19", "yjxjoqzqm6lt7prqsh9aquxxc", "31lusu76ql6l2ezxwssua2ds3btq", "31ikcd2nl4ryblwijksmu7i6awre", "31ye6qli2rdghsvzvk7ebxwzrqpe", "owr9wpz6h19imxf0x4kxtxdxz", "02l516u6cz4qni0vqehtegmbx", "wb09hvocyvva4rmrga98d5ql5", "2b516vb26kzyfwrb6j97v78n9", "313ijm464m74npcybd2c6t2rfkzq", "31mt3xhu6pahb4qs2odsboqgliwy", "314vj3wnsjfh3eldvb34iezpxg6a", "31ihofttbm63ibjjnyfl5vcbjpfm", "312sl2yo5c3gvbsfqjuxsrba7cya", "cgg0skpqzwd414xar7leoe6cl", "31tlqt22dsqxny34ze3rv5j5nebe", "314inzavxlbbcauh2q4yf3qw6rsq", "erw2iikv1lxmut0vzp4eguknp", "31yk62hn5jmd6nrbahf7ie7qjbtu", "31kswwjxmjpigdm2br7fmp7logla", "315w4ce6ycoluwlai7by77ptem4i", "31fpcctbthki5a2zfyliqcgl7szu", "31fdaw7no6u34is3ktrulsitzgmq", "31gr7mocmbtwedzxpgrdkwepyagy", "31twf5hs72ojksvitj7zghj2epr4", "313i3yokfg2wfjxaosmc4axfkndm", "31my657ebw6rbt5qd2lmnokkzukq", "313gn2siq2nkaqspkr3bfguvpyva", "eom65t8uj4n3fz7kmbgvxuhxv", "31toqobny6ei7546tmyvvz4g6ysy", "31lr4tqolutgtrjkaurzhtowxjly", "31ehk7iom6azvyaurbfnz3dcn2je", "31lojcpro3uhr63334esjvnal3gm", "31f7dowblu65o5tm2ytlihfpmcja", "31tucvl2ejkbyt6tj4slaf4v3i4e", "t4teanpfoiyrn4at7mctazhw4", "gi5fbnzmuml5uusenyx9njv2h", "3z1swo9zojhc68mdb9ramdull", "31j2nu3u44kwrpgdirqjapn3jwzu", "31j4hbrc36h6zxlv2qeqwk63wes4", "31vq67blyvtehgstkxh5brg5dgqy", "g7utx93l5a99foqd8cv7hxav9", "db44hkhq5kud5dsvgj90j29t1", "31ymuf4e3ketijjpofpdaklbqoha", "ch23205ctn4hnudavam94uzna", "31fi3em22ipnpoputnuwynlq5kom", "445b38m2srygwmtiab287l6ax", "31ej57yidxz6cqypakllijdnnbu4", "31wxvin5xepzehbzjc6sjvttzfom", "217pnmdkvn4ae7ex5tkcwgkmq", "31iixaqmzoescqp3pz3majvu7lwq", "qn1iwxzzr1c04m56nra1tlzo9", "3152tuxmvlqymw2wt7kwqlaiavny", "31knxj7mgxweegbfkumspcpvw3ke", "s0vncc3f5t0tmwepihj6jk5ar", "31nbkopbkcugjp6j46wdp3xoz4uq", "5zkx1upmyabkhuknf6ovgrov2", "q4y56toadukdjkeb7i0bq2ow1", "31fbl2g2jr4dtevb4mwgkj5e66oq", "jvdcnf37gdg6wxkvs7ten0y3o", "ndw6w274kz385rwvi1mmz48sw", "31avwb4cce5o3dbids5oikyvp5x4", "31riqggtfurugyftql44zpuk3m6e", "31rfcdpjksqpeo5y6yuvuo3zmt4e", "srap1bfq2r0eskfyrkx7xpgel", "lri7cbokx2bjyuxy2kavyd78d", "0fjfu2jdhuljjxzp0knkd2mc9", "31mo2oq2j77kz77nqbqueauwalzi", "315fflmmp34lkxatkhpc7nvfwiaq", "r0tmmvke3s0818p8dlrbkoref", "richrdkurniawn", "31uileq5qbtgcikphrbe5ucxo6eq", "31pugsla4gauucuc5wfsp7xzke7u", "31z7tbqpjvtomghuquocdpneuycu", "31ram3rgemablu2spiwksojatsje", "5eukieegnx1a4wzq5dlrsio1k", "r3ewjmygfvmj4591kc8wig4bb", "31bym3mguccsq5m3ftnren7dpdgm", "316zprr7gltvre2jd7svsru7qy4m", "z255f15mvknq0dpv0dh6chh26", "31ims77ozszzvoff75yvf4r2evde", "31e25zo5cg2lf6jmfp6q2fbknd3a", "21ihwxezo7lywxyqee3se7ixi", "anaskachandra", "bol4t3ys5nk3p42wto27p94cy", "31jgkq6gxsnjjikpl7fndttr2t4a", "gma1mcz1vs6s8l0z5axapw1v9", "6rl4oiocv9a5b9ri6zzpu0bib", "31ikhcrdz4qsk22dp2kvofavwqna", "31y3tc4nfw2gnvyy7k6jflf3nhmq", "sdvg0pggwlgqwu49efnzakdfk", "31khl6fq77jw5f33aoef36r3vddq", "7dhuxwoevwnaoscngirypiffi", "31pzxv6t5xlh724ur6mt7fkj6o6e", "1g3nzpqwfq3amvqfhxdd3guct", "smo7u3pm1wl017tj3beqd04ww", "oiimxrye9ue9qa43g7kmef0x0", "3133i2zxyzfzn6vy3mm2xx5hq77i", "x5un65a3nt9wai8o0f35jbyhx", "rtmf440t2kvczvtvajd1lcf2d", "31xhi5ffvjbwjeofl5owrq7oexve", "316nzj4uhpjamwlhhgknrvjlt3dy", "31yqiwjnzlj5mdjozkacvlppqn7m", "31mibgus5qifdvdymscnz4wiee6q", "31hqc53svove3wxdxbttsuwnwolu", "4fiaaj60p5wrtxq90aff6eepa", "obg55uhsjatc796sxtrcc3o16", "31mpiqgdzf76wcvgvlbu7fj55jxu", "59xk8c2nh8dkyyd3kl6xtrisk", "31u7dalmxf2q6vmd7r3h2mlad6ay", "9qo2jd888xx6g6oh836xdjbzc", "ihseeyu5daa0l661x9nrr08w6", "313kfmev4ikkpngfdbyur7ngfrue", "31momaetuzrv5z4va5vikwzutsou", "31jt2mbieew4hxatagtduvrcmmva", "31mr5n2kctqgtsbyuuf2pxgn2fwe", "31irmf7o3nsjofpr4pxyda7hpwu4", "31emw4kib6l4gqrrp4ea2gm3f5zq", "yrgktf8clvcas2et2za3fdftx", "31a236jzywk7e24d3nkdjcysdxtu", "q238ynw5c218ern00pucg6a5j", "3132b2t4h6rxbayw7udirgbpdyba", "31tjhmhymhctwmm4emkkxghkqeoq", "jplkkqun2b29w5fs1n8r0xfcq", "31iencsxzwxmtorukemd7naiuu6m", "31tcmi6ou7uhstp3oenwy3ktog6e", "thesoundsofspotify", "31knidxspstgity33dq225rljawa", "31knrkesbmdjpr5dey5vctbzlcku", "31kuqmrp4y4qlc6unmahnfbmnyty", "31ey7pwluroi2jtsqicezjeh2m34", "pn2vesv93a5q269r34lccpkez", "31ytcsf3t7nlspzu4ti2pmdbtq4i", "31ylxjygzhuin4zf2ptxugttz4ay", "31tatuynz3yaubleumhux2grpgom", "31h7fyhs2yzuty6dqkwe3mfjuwqi", "31tx2wbxwjo7e73exgl2q5as4xha", "31vfqi547vy26k7g6pahinzseude"]

client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# SQLite database file paths
playlists_db_path = config['db']['playlists_db']
songs_db_path = config['db']['songs_db']


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn


def save_playlist_to_database(user_id, playlist_id, conn):
    try:
        playlist = sp.playlist(playlist_id)

        if playlist['tracks']['total'] <= 5:
            print(f"Skipping playlist {playlist_id}, not enough tracks.")
            return

        cursor = conn.cursor()
        cursor.execute('''INSERT OR IGNORE INTO playlists (playlist_id, creator_id, original_track_count)
                          VALUES (?, ?, ?)''',
                       (playlist_id, user_id, playlist['tracks']['total']))
        conn.commit()

        tracks = playlist['tracks']['items'][:66]
        playlist_items = ','.join([track['track']['id'] for track in tracks])

        cursor.execute('''INSERT OR REPLACE INTO items (playlist_id, playlist_items)
                          VALUES (?, ?)''',
                       (playlist_id, playlist_items))
        conn.commit()

        insert_track_ids_into_tracks(tracks)
        insert_artist_ids_into_artists(tracks)

        print(f"Saved playlist details for {playlist_id}")
        time.sleep(float(config['api']['delay_time']))

    except SpotifyException as e:
        if e.http_status == 429:
            print(f"Rate limit exceeded. Last processed playlist: {
                  playlist_id}")
        else:
            print(f"Spotify error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def insert_track_ids_into_tracks(tracks):
    conn = create_connection(songs_db_path)
    cursor = conn.cursor()

    for track_item in tracks:
        track_id = track_item['track']['id']
        cursor.execute(
            "INSERT OR IGNORE INTO tracks (track_id) VALUES (?)", (track_id,))

    conn.commit()
    conn.close()


def insert_artist_ids_into_artists(tracks):
    conn = create_connection(songs_db_path)
    cursor = conn.cursor()

    for track_item in tracks:
        artists = track_item['track']['artists']
        for artist in artists:
            artist_id = artist['id']
            cursor.execute(
                "INSERT OR IGNORE INTO artists (artist_id) VALUES (?)", (artist_id,))

    conn.commit()
    conn.close()


fetched_users_file = config['file']['fetched_users']
try:
    with open(fetched_users_file, 'r') as f:
        fetched_users = set(f.read().splitlines())
except FileNotFoundError:
    fetched_users = set()

for user_id in user_ids:
    if user_id in fetched_users:
        print(f"Skipping {user_id}, already fetched.")
        continue

    conn = create_connection(playlists_db_path)
    if conn is not None:
        try:
            offset = 0
            limit = 50  # Spotify API maximum limit per request is 50
            while True:
                playlists = sp.user_playlists(
                    user_id, offset=offset, limit=limit)
                if not playlists['items']:
                    break

                for playlist in playlists['items']:
                    if playlist['public']:
                        playlist_id = playlist['id']
                        save_playlist_to_database(user_id, playlist_id, conn)

                offset += limit  # Move to the next batch of playlists

            fetched_users.add(user_id)

        except SpotifyException as e:
            if e.http_status == 429:
                print(f"Rate limit exceeded. Last processed user: {user_id}")
            else:
                print(f"Spotify error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        conn.close()
    else:
        print("Error! Cannot create the database connection.")

with open(fetched_users_file, 'w') as f:
    for user_id in fetched_users:
        f.write(user_id + '\n')

print("Scrape completed.")
