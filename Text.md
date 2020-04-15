## Diplomová práce 

### Cíl: Využít evolučních algoritmů pro vývoj komponenty svítidel veřejného osvětlení

Ve svítidlech veřejného osvětlení se nacházejí reflektorky - komponenty z reflektorového plechu, 
které slouží ke správnému směrování světla z LED a zvýšení účinnosti svítidla. 

Cílem práce je využím evolučních algoritmů pro navržení tvaru reflektorku, kteý bude splňovat následující:

* Co nejvíce světla z diody bude směřováno pod svítidlo do určené oblasti, aby byla **účinnost** co nejvyšší

* Co nejvíce paprsků bude dopadat na povrch nepřímo - budou **odražené** od reflektorového plechu nikoli přímo z LED

* Paprsky budu na povrch dopadat co **nejrovnoměrněji**

### Postup

* [x] Namodelovat základní prostředí - simulace LED s 15 paprsky, jedna odrazivá laple, mutace - měnění úhlu laple, vykreslování do svg

* [x] Fitness - fitness založena na počtu paprsků dopadající na silnici případně na počtu odražených paprsků od laple

* [x] Progress - batchové konvertování výsledků do png, vytvoření .avi videa 

* [x] Věrnější simulace - dvě odrazivé laple, paprsky s více odrazy

* [x] Rovnoměrnost paprsků - vyzkoušení několika způsobů hodnocení rovnoměrného dopadu paprsků

* [x] Úprava evoluce - přidání další mutace - změna délky laplí, udržování nejlepšího jedince



