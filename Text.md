## Diplomová práce 

### Cíl: Využít evolučních algoritmů pro vývoj komponenty svítidel veřejného osvětlení

Ve svítidlech veřejného osvětlení se nacházejí reflektorky - komponenty z reflektorového plechu, 
které slouží ke správnému směrování světla z LED a zvýšení účinnosti svítidla. 

Cílem práce je využít evolučních algoritmů pro navržení tvaru reflektorku, kteý bude splňovat následující:

* Co nejvíce světla z diody bude směřováno pod svítidlo do určené oblasti, aby byla **účinnost** co nejvyšší

* Co nejvíce paprsků bude dopadat na povrch nepřímo - budou **odražené** od reflektorového plechu nikoli přímo z LED

* Paprsky budu na povrch dopadat co **nejrovnoměrněji**

Musí být možné návrh vyrobit a otestovat v praxi!! 

### Postup

* [x] Namodelovat základní prostředí - simulace LED s 15 paprsky, jedna odrazivá laple, mutace - měnění úhlu laple, vykreslování do svg

* [x] Fitness - fitness založena na počtu paprsků dopadající na silnici případně na počtu odražených paprsků od laple

* [x] Progress - batchové konvertování výsledků do png, vytvoření .avi videa 

* [x] Věrnější simulace - dvě odrazivé laple, paprsky s více odrazy

* [x] Rovnoměrnost paprsků - vyzkoušení několika způsobů hodnocení rovnoměrného dopadu paprsků

* [x] Úprava evoluce - přidání další mutace - změna délky laplí, udržování nejlepšího jedince

* [ ] Vícekriteriální optimalizace - vyzkoušet NSGAII 

* [ ] Zaznamenávání postupu - Data o výsledcích, obrázky, videa

* [ ] Úprava evoluce - aby v ní bylo více explorace a různorodosti - **Konzultace**

* [ ] Lambertian distribution - generování zadanáho počtu paprsků tak, aby rozdělení odpovídalo LED zdroji - **Konzultace**

* [ ] Úprava laplí - přidání možnosti 1 - 2 ohybů laple

* [ ] Parametry - úprava programu, aby se všechny parametry daly nastavit například v JSONu

* [ ] Komentáře - okomentování programu, úprava

* [ ] Konzultace optika - konzultace výsledků v práci, zvážení úprav

* [ ] Vyrobení prototypu - ověření výroby, měření, zhodnocení - **Do konce dubna**
