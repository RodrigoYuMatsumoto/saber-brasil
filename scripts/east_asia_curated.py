"""Recortes editoriais multilíngues; cada linha exige uma âncora primária."""

# País|componente|anos de procura|domínio. Linhas: nome pt-BR|nome inglês|âncora nativa|nome zh-Hant.
CURATED = r"""
JP|matematica|1|Números e contagem
Comparação de coleções|Comparing collections|個数を比べる|比較物件數量
Contagem e ordem|Counting and order|順番|計數與順序
Posição na reta numérica|Position on a number line|数直線|數線上的位置
Composição de números|Composing numbers|和や差|數的組成
Números de dois algarismos|Two-digit numbers|２位数|兩位數
Centenas em casos simples|Simple hundreds|３位数|簡單的百位數
Agrupamentos de dez|Groups of ten|十を単位|以十為單位
Partilha de coleções|Sharing collections|等分|平均分配物件
Significado da adição|Meaning of addition|加法及び減法の意味|加法的意義
Significado da subtração|Meaning of subtraction|加法及び減法の意味|減法的意義
Expressões de adição e subtração|Addition and subtraction expressions|式に表し|加減法算式
Cálculo com um algarismo|Single-digit calculation|１位数と１位数|一位數計算
Formas do cotidiano|Everyday shapes|形の特徴|日常形狀
Construção e decomposição de formas|Composing and splitting shapes|形を作ったり分解|組合與分解形狀
Direção e posição espacial|Spatial direction and position|方向や位置|空間方向與位置
Comparação de comprimentos|Comparing lengths|長さ，広さ，かさ|比較長度
Leitura de horas simples|Reading simple clock times|時刻|讀取簡單時刻
Representação de quantidades em imagens|Pictorial quantity displays|絵や図|以圖像表示數量

JP|matematica|2|Cálculo e medidas
Números até quatro algarismos|Numbers with up to four digits|４位数|四位數以內的數
Centenas e milhares|Hundreds and thousands|百，千|百與千
Somas em coluna|Column addition|筆算|直式加法
Multiplicação como agrupamento|Multiplication as grouping|乗法の意味|乘法與分組
Tabuada|Multiplication facts|乗法九九|九九乘法表
Relação entre adição e subtração|Addition and subtraction relationship|加法と減法の相互関係|加減法的關係
Triângulos e quadriláteros|Triangles and quadrilaterals|三角形や四角形|三角形與四邊形
Ângulo reto|Right angles|直角|直角
Quadrado e retângulo|Squares and rectangles|正方形，長方形|正方形與長方形
Sólidos em forma de caixa|Box-shaped solids|箱の形|箱形立體
Milímetros, centímetros e metros|Millimetres centimetres and metres|mm|毫米公分與公尺
Mililitros e litros|Millilitres and litres|mL|毫升與公升
Duração e intervalo de tempo|Duration and elapsed time|時間|時間長度與間隔
Tabelas e gráficos simples|Simple tables and graphs|表やグラフ|簡單表格與圖表

JP|matematica|3|Operações e representação
Números de cinco algarismos|Five-digit numbers|万の単位|五位數
Divisão e seus contextos|Division and its contexts|除法の意味|除法的意義
Relação entre multiplicação e divisão|Multiplication and division relationship|乗法や減法との関係|乘除法的關係
Resto na divisão|Remainders|余り|除法的餘數
Multiplicação por dois algarismos|Multiplication by two-digit numbers|２位数の乗法|兩位數乘法
Adição e subtração de decimais|Adding and subtracting decimals|小数の加法及び減法|小數加減法
Frações unitárias|Unit fractions|単位分数|單位分數
Representação de frações|Representing fractions|分数|分數的表示
Triângulos isósceles e equiláteros|Isosceles and equilateral triangles|二等辺三角形，正三角形|等腰與正三角形
Círculo e esfera|Circles and spheres|円や球|圓與球
Quilómetros e distâncias|Kilometres and distances|km|公里與距離
Gramas e quilogramas|Grams and kilograms|kg|公克與公斤
Gráficos de barras|Bar charts|棒グラフ|長條圖
Pesquisas e classificação de dados|Surveys and data classification|分類整理|調查與資料分類

JP|matematica|4|Frações, área e variação
Números grandes e ordens|Large numbers and place value|億，兆|大數與位值
Arredondamento e estimativa|Rounding and estimation|概数|概數與估算
Divisão escrita|Written division|除法の筆算|除法直式
Frações equivalentes em comparação|Comparing equivalent fractions|大きさの等しい分数|等值分數的比較
Frações de mesmo denominador|Fractions with a common denominator|同分母の分数|同分母分數
Perpendicularidade e paralelismo|Perpendicular and parallel lines|垂直及び平行|垂直與平行
Paralelogramos e losangos|Parallelograms and rhombuses|平行四辺形，ひし形|平行四邊形與菱形
Cubos e paralelepípedos|Cubes and cuboids|立方体，直方体|正方體與長方體
Área do retângulo|Area of a rectangle|面積の求め方|長方形面積
Unidades de área|Units of area|cm2|面積單位
Medição de ângulos|Measuring angles|角の大きさ|測量角度
Mudanças em gráficos de linhas|Changes in line graphs|折れ線グラフ|折線圖中的變化
Tabelas de duas entradas|Two-way tables|二つの観点|雙向表

JP|matematica|5|Proporção e geometria
Múltiplos e divisores|Multiples and factors|約数，倍数|倍數與因數
Números pares e ímpares|Even and odd numbers|偶数，奇数|偶數與奇數
Multiplicação de decimais|Multiplying decimals|小数の乗法|小數乘法
Divisão de decimais|Dividing decimals|小数の乗法及び除法|小數除法
Frações com denominadores diferentes|Fractions with unlike denominators|異分母|異分母分數
Congruência de figuras|Congruent shapes|合同|全等圖形
Polígonos regulares|Regular polygons|正多角形|正多邊形
Razão entre circunferência e diâmetro|Circumference and diameter ratio|円周率|圓周率
Prismas e cilindros|Prisms and cylinders|角柱や円柱|角柱與圓柱
Volume de cubos e paralelepípedos|Volumes of cubes and cuboids|体積の求め方|正方體與長方體體積
Média aritmética|Arithmetic mean|平均|算術平均
Quantidade por unidade|Quantity per unit|単位量当たり|單位量
Velocidade e grandezas relacionadas|Speed and related quantities|速さ|速度及相關量
Percentagens e proporções|Percentages and proportions|百分率|百分率與比例

JP|matematica|6|Frações e análise de dados
Multiplicação de frações|Multiplying fractions|分数の乗法|分數乘法
Divisão de frações|Dividing fractions|分数の乗法及び除法|分數除法
Relações expressas por letras|Relationships expressed with letters|文字を用い|以字母表示關係
Ampliação e redução de figuras|Enlarging and reducing shapes|縮図や拡大図|圖形的縮小與放大
Simetria axial e central|Line and point symmetry|対称な図形|軸對稱與點對稱
Área do círculo|Area of a circle|円の面積|圓的面積
Volume de prismas e cilindros|Volumes of prisms and cylinders|角柱及び円柱の体積|角柱與圓柱體積
Proporcionalidade direta|Direct proportion|比例の関係|正比例
Proporcionalidade inversa|Inverse proportion|反比例|反比例
Razões entre grandezas|Ratios between quantities|比の意味|比的意義
Distribuição e representatividade|Distributions and representative values|代表値|分布與代表值
Gráficos de frequências|Frequency diagrams|度数分布|次數分布圖
Organização de possibilidades|Organising possible outcomes|場合を順序よく|有序整理可能情況

JP|matematica|7-9|Álgebra e geometria do secundário inferior
Números positivos e negativos|Positive and negative numbers|正の数と負の数|正數與負數
Operações com inteiros|Integer operations|四則計算|整數運算
Expressões algébricas|Algebraic expressions|文字を用いた式|代數式
Equações de primeiro grau|Linear equations|一元一次方程式|一元一次方程
Proporção em tabelas e gráficos|Proportion in tables and graphs|比例，反比例|比例的表格與圖像
Construções geométricas|Geometrical constructions|作図|幾何作圖
Transformações de figuras|Geometrical transformations|図形の移動|圖形變換
Planificações de sólidos|Nets of solids|展開図|立體展開圖
Probabilidade experimental|Experimental probability|多数の観察|實驗機率
Sistemas de equações|Simultaneous equations|連立二元一次方程式|二元一次聯立方程
Função afim|Linear functions|一次関数|一次函數
Propriedades de triângulos|Properties of triangles|三角形の合同条件|三角形的性質
Demonstração geométrica|Geometric proof|証明|幾何證明
Probabilidade por contagem|Probability by counting|確率|以計數求機率
Raízes quadradas|Square roots|平方根|平方根
Polinómios e fatoração|Polynomials and factorisation|因数分解|多項式與因式分解
Equações quadráticas|Quadratic equations|二次方程式|二次方程
Semelhança de figuras|Similar shapes|相似|相似圖形
Teorema de Pitágoras|Pythagorean theorem|三平方の定理|畢氏定理
Amostragem estatística|Statistical sampling|標本調査|統計抽樣

JP|ciencias|3|Observação de materiais e seres vivos
Massa e forma dos objetos|Mass and shape of objects|重さ|物體的質量與形狀
Materiais diferentes e massa|Materials and mass|材質|不同材料與質量
Força do vento|Wind force|風の力|風力
Força da borracha elástica|Elastic rubber force|ゴムの力|橡皮筋的力
Reflexão da luz|Light reflection|光を当て|光的反射
Luz e aquecimento|Light and heating|温かさ|光與加熱
Produção e transmissão do som|Producing and transmitting sound|音|聲音的產生與傳播
Propriedades dos ímanes|Properties of magnets|磁石|磁鐵的性質
Circuitos elétricos simples|Simple electric circuits|電気を通す|簡單電路
Crescimento de insetos|Insect growth|昆虫|昆蟲的生長
Partes das plantas|Parts of plants|植物の育ち方|植物的部位
Sol, sombra e superfície terrestre|Sun shadows and ground|太陽と地面|太陽影子與地面

JP|ciencias|4|Corpo, água e ambiente
Ossos e músculos|Bones and muscles|骨と筋肉|骨骼與肌肉
Variações sazonais de plantas|Seasonal changes in plants|季節|植物的季節變化
Atividade dos animais nas estações|Animal activity across seasons|動物の活動|動物的季節活動
Percurso da água no solo|Water movement in soil|雨水|雨水在土壤中的流動
Volume e pressão do ar|Air volume and pressure|空気の体積|空氣體積與壓力
Expansão térmica dos materiais|Thermal expansion|体積や温度|材料的熱膨脹
Propagação de calor nos metais|Heat transfer in metals|金属|金屬中的熱傳遞
Estados físicos da água|States of water|水の三態変化|水的三態變化
Evaporação e condensação|Evaporation and condensation|蒸発|蒸發與凝結
Variações do tempo atmosférico|Weather changes|天気の様子|天氣變化
Movimento aparente da Lua|Apparent movement of the Moon|月や星|月亮的視運動
Estrelas e constelações|Stars and constellations|星の明るさ|恆星與星座

JP|ciencias|5|Investigação científica
Dissolução de substâncias|Dissolving substances|物の溶け方|物質溶解
Conservação da massa na dissolução|Mass conservation in solutions|重さは変わらない|溶解時的質量守恆
Condições de solubilidade|Conditions affecting solubility|水の温度|影響溶解度的條件
Período do pêndulo|Pendulum period|振り子|擺的週期
Eletroímanes|Electromagnets|電磁石|電磁鐵
Germinação das sementes|Seed germination|発芽|種子發芽
Crescimento das plantas|Plant growth|植物の成長|植物生長
Polinização e formação de sementes|Pollination and seed formation|受粉|授粉與種子形成
Desenvolvimento de peixes|Fish development|魚の誕生|魚類的發育
Desenvolvimento humano|Human development|人の誕生|人的發育
Erosão e transporte por rios|River erosion and transport|流れる水|流水侵蝕與搬運
Nuvens e previsão do tempo|Clouds and weather forecasting|雲|雲與天氣預報

JP|ciencias|6|Sistemas e transformações
Combustão e ar|Combustion and air|燃焼|燃燒與空氣
Propriedades das soluções aquosas|Properties of aqueous solutions|水溶液|水溶液的性質
Ácidos e álcalis|Acids and alkalis|酸性|酸與鹼
Equilíbrio das alavancas|Lever equilibrium|てこ|槓桿平衡
Produção e utilização da eletricidade|Generating and using electricity|発電|發電與用電
Armazenamento de energia elétrica|Storing electrical energy|蓄電|儲存電能
Respiração e circulação|Respiration and circulation|呼吸|呼吸與循環
Digestão e absorção|Digestion and absorption|消化|消化與吸收
Fotossíntese e produção de amido|Photosynthesis and starch|でんぷん|光合作用與澱粉
Água no corpo das plantas|Water in plants|水の通り道|植物體內的水
Cadeias alimentares|Food chains|食べ物|食物鏈
Formação de camadas do solo|Formation of geological layers|地層|地層的形成
Vulcões e sismos|Volcanoes and earthquakes|火山|火山與地震
Fases da Lua|Phases of the Moon|月の形|月相

JP|ciencias|7-9|Ciências do secundário inferior
Refração da luz|Refraction of light|屈折|光的折射
Forças e deformações|Forces and deformation|力の働き|力與形變
Densidade das substâncias|Density of substances|密度|物質密度
Separação de misturas|Separating mixtures|蒸留|混合物的分離
Mudanças de estado|Changes of state|状態変化|物態變化
Vulcões e rochas|Volcanoes and rocks|火成岩|火山與岩石
Estratos e fósseis|Strata and fossils|化石|地層與化石
Eletricidade e resistência|Electricity and resistance|抵抗|電與電阻
Correntes elétricas e magnetismo|Electric current and magnetism|磁界|電流與磁場
Átomos e moléculas|Atoms and molecules|原子や分子|原子與分子
Reações químicas|Chemical reactions|化学変化|化學反應
Células e organismos|Cells and organisms|細胞|細胞與生物
Sistemas do corpo humano|Human body systems|消化や呼吸|人體系統
Humidade e formação de nuvens|Humidity and cloud formation|湿度|濕度與雲的形成
Movimento e energia|Motion and energy|運動とエネルギー|運動與能量
Iões e eletrólitos|Ions and electrolytes|イオン|離子與電解質
Reprodução e hereditariedade|Reproduction and heredity|遺伝|生殖與遺傳
Sistema Solar e estrelas|Solar system and stars|太陽系|太陽系與恆星
Ecossistemas e ação humana|Ecosystems and human activity|自然環境|生態系與人類活動

JP|japones|1-2|Leitura e escrita iniciais
Hiragana|Hiragana|平仮名|平假名
Katakana|Katakana|片仮名|片假名
Kanji dos anos iniciais|Early elementary kanji|漢字|小學初階漢字
Sons e sílabas do japonês|Japanese sounds and syllables|音節|日語語音與音節
Escrita e ordem dos traços|Writing and stroke order|筆順|書寫與筆順
Leitura em voz alta|Reading aloud|音読|朗讀
Sequência de acontecimentos|Sequence of events|順序|事件順序
Identificação de personagens|Identifying characters|登場人物|辨認人物
Escuta e turnos de fala|Listening and turn-taking|話し手|聆聽與輪流發言

JP|japones|3-4|Texto e linguagem
Uso do dicionário|Using dictionaries|辞書|使用字典
Rōmaji|Romaji|ローマ字|羅馬字
Estrutura de parágrafos|Paragraph structure|段落|段落結構
Ideia central e detalhes|Main ideas and details|中心となる語|主旨與細節
Comparação de informações|Comparing information|比較|比較資訊
Organização de relatos|Organising reports|報告|整理報告
Expressão de opiniões|Expressing opinions|考えとそれを支える|表達意見
Leitura de poemas|Reading poems|詩|閱讀詩歌

JP|japones|5-6|Argumentação e cultura escrita
Relações entre palavras|Relationships between words|語句と語句|詞語之間的關係
Resumo de informações|Summarising information|要旨|概括資訊
Factos e opiniões|Facts and opinions|事実と感想|事實與意見
Estrutura de argumentos|Argument structure|主張|論證結構
Comparação de fontes|Comparing sources|複数の本|比較資料來源
Linguagem formal e cortesia|Formal and polite language|敬語|敬語與禮貌表達
Textos clássicos japoneses|Classical Japanese texts|古文|日本古典文章
Debate e fundamentação|Discussion and justification|話し合|討論與論據

JP|estudos-sociais|3-6|Sociedade e território japoneses
Mapeamento do município|Mapping the local municipality|市の様子|繪製市區地圖
Trabalho e comércio local|Local work and commerce|販売|地方工作與商業
Serviços de segurança|Safety services|警察|安全服務
História e mudanças do município|Changes in the municipality|移り変わり|地方歷史與變遷
Abastecimento de água|Water supply|飲料水|供水
Destino dos resíduos|Waste management|廃棄物|廢棄物處理
Prevenção de desastres locais|Local disaster prevention|自然災害|地方防災
Património cultural regional|Regional cultural heritage|文化財|地方文化資產
Território e relevo do Japão|Japanese territory and relief|国土の地形|日本國土與地形
Agricultura e pesca japonesas|Japanese agriculture and fishing|農業|日本農業與漁業
Indústria e transportes|Industry and transport|工業|工業與交通
Informação e vida social|Information in society|情報|資訊與社會生活
Constituição e vida nacional|Constitution and national life|日本国憲法|憲法與國民生活
História antiga do Japão|Ancient Japanese history|大和朝廷|日本古代史
Período Nara e budismo|Nara period and Buddhism|奈良|奈良時代與佛教
Governo dos samurais|Samurai governments|武士|武士政權
Período Edo|Edo period|江戸幕府|江戶時代
Modernização Meiji|Meiji modernisation|明治|明治維新與近代化
Guerra e paz no século XX|War and peace in the twentieth century|戦争|二十世紀的戰爭與和平
Relações internacionais do Japão|Japan's international relations|国際交流|日本的國際關係

JP|geografia|7-9|Geografia do secundário inferior
Continentes e oceanos|Continents and oceans|大陸|大洲與海洋
Latitude e longitude|Latitude and longitude|緯度と経度|緯度與經度
Climas e modos de vida|Climate and ways of life|気候|氣候與生活方式
População e cidades|Population and cities|人口|人口與城市
Recursos e energia|Resources and energy|資源|資源與能源
Regiões do Japão|Regions of Japan|日本の諸地域|日本各地區
Leitura de mapas topográficos|Reading topographic maps|地形図|閱讀地形圖
Investigação geográfica local|Local geographical inquiry|地域調査|地方地理調查

JP|historia|7-9|História japonesa e mundial
Vestígios e fontes históricas|Historical remains and sources|資料|遺跡與史料
Antigas civilizações|Ancient civilisations|古代文明|古代文明
Formação do Estado japonês|Formation of the Japanese state|国家の形成|日本國家的形成
Sociedade medieval japonesa|Medieval Japanese society|中世|日本中世社會
Expansão dos contactos mundiais|Expanding global contacts|ヨーロッパ|全球交流擴展
Industrialização e mundo moderno|Industrialisation and the modern world|産業革命|工業革命與近代世界
Japão na ordem internacional moderna|Japan in the modern international order|近代|近代國際秩序中的日本
Democracia e Japão do pós-guerra|Democracy and post-war Japan|民主化|戰後日本與民主化

JP|educacao-moral|1-6|Convivência e vida moral
Honestidade|Honesty|正直|誠實
Responsabilidade e autonomia|Responsibility and autonomy|責任|責任與自主
Respeito e cortesia|Respect and courtesy|礼儀|尊重與禮貌
Amizade e confiança|Friendship and trust|友情|友誼與信任
Cuidado com a vida|Care for life|生命|珍惜生命
Natureza e seres vivos|Nature and living beings|自然愛護|愛護自然與生命
Regras e bem comum|Rules and the common good|規則|規則與共同利益
Respeito por outras culturas|Respect for other cultures|国際理解|尊重其他文化

JP|economia-domestica|5-6|Vida doméstica
Vida familiar e cooperação|Family life and cooperation|家族|家庭生活與合作
Organização do trabalho doméstico|Organising household work|家庭の仕事|家務工作的安排
Preparação de alimentos|Food preparation|調理|食物烹調
Refeições equilibradas|Balanced meals|栄養|均衡飲食
Confeção e reparação têxtil|Making and repairing textiles|縫|紡織品製作與修補
Roupas e cuidado pessoal|Clothing and personal care|衣服|衣著與個人照護
Consumo e orçamento|Consumption and budgeting|金銭|消費與預算
Consumo e ambiente|Consumption and environment|環境|消費與環境

JP|tecnologia|7-9|Tecnologia e vida doméstica
Propriedades dos materiais|Properties of materials|材料|材料性質
Desenho e fabricação|Design and manufacture|製作|設計與製作
Cultivo de organismos|Cultivating living organisms|生物育成|生物培育
Conversão de energia|Energy conversion|エネルギー変換|能量轉換
Redes e informação digital|Networks and digital information|ネットワーク|網絡與數碼資訊
Programação e controlo|Programming and control|プログラミング|程式設計與控制
Segurança da informação|Information security|情報セキュリティ|資訊安全
Sustentabilidade tecnológica|Technological sustainability|持続可能|科技與永續發展

JP|arte|1-6|Música e artes visuais
Ritmo e pulsação musical|Rhythm and pulse|リズム|節奏與拍子
Melodia e canto|Melody and singing|旋律|旋律與歌唱
Instrumentos e timbres|Instruments and timbre|音色|樂器與音色
Criação musical|Creating music|音楽づくり|音樂創作
Escuta musical|Musical listening|鑑賞|音樂欣賞
Formas e cores nas artes|Shapes and colours in art|形や色|藝術中的形狀與色彩
Expressão com materiais|Expression through materials|材料|材料表現
Criação tridimensional|Three-dimensional creation|立体|立體創作

JP|educacao-fisica|1-6|Movimento e educação física
Equilíbrio e controlo corporal|Balance and body control|体のバランス|平衡與身體控制
Correr e saltar|Running and jumping|走|跑與跳
Jogos com bola|Ball games|ボール|球類遊戲
Movimentos aquáticos|Water movement|水|水中活動
Movimento rítmico|Rhythmic movement|リズム|韻律動作
Ginástica com aparelhos|Apparatus gymnastics|器械|器械體操
Saúde e hábitos cotidianos|Health and daily habits|健康|健康與日常習慣
Segurança na atividade física|Safety in physical activity|安全|運動安全

JP|ingles|3-6|Comunicação em língua estrangeira
Escuta de palavras familiares|Listening to familiar words|聞くこと|聆聽熟悉詞語
Conversas e cumprimentos|Conversation and greetings|挨拶|對話與問候
Apresentação pessoal|Introducing oneself|自己紹介|自我介紹
Expressão de gostos|Expressing preferences|好き|表達喜好
Perguntas sobre o cotidiano|Questions about daily life|質問|日常生活提問
Leitura de palavras familiares|Reading familiar words|読むこと|閱讀熟悉詞語
Escrita de palavras e expressões|Writing words and expressions|書くこと|書寫詞語與短句
Culturas e comunicação|Cultures and communication|文化|文化與溝通

CN|matematica|1-2|Números e operações iniciais
Contagem e comparação de quantidades|Counting and comparing quantities|数的认识|計數與數量比較
Números naturais e representação|Natural numbers and representation|数的认识|自然數及其表示
Valor posicional decimal|Decimal place value|十进制|十進位值
Adição e subtração iniciais|Early addition and subtraction|加法|初階加減法
Multiplicação como agrupamento|Multiplication as grouping|乘法|乘法與分組
Divisão e partilha|Division and sharing|除法|除法與平均分配
Cálculo mental simples|Simple mental calculation|口算|簡單心算
Situações de cálculo no cotidiano|Everyday calculation situations|运算|日常計算情境
Padrões de repetição|Repeating patterns|规律|重複規律
Direções e posições|Directions and positions|位置|方向與位置
Formas planas e sólidas|Plane and solid shapes|图形|平面與立體圖形
Comprimento e medição|Length and measurement|长度|長度與測量
Horas e calendário|Time and calendar|时间|時間與日曆
Classificação de dados|Classifying data|分类|資料分類

CN|matematica|3-4|Cálculo e geometria
Números grandes|Large numbers|万以上|大數
Operações com números naturais|Natural number operations|四则运算|自然數四則運算
Propriedades das operações|Properties of operations|运算律|運算定律
Introdução aos decimais|Introduction to decimals|小数|小數入門
Significado das frações|Meaning of fractions|分数|分數的意義
Adição e subtração de frações|Adding and subtracting fractions|同分母|分數加減法
Multiplicação e divisão escritas|Written multiplication and division|笔算|乘除法筆算
Perímetro de figuras|Perimeters of shapes|周长|圖形周長
Área do quadrado e retângulo|Area of squares and rectangles|面积|正方形與長方形面積
Ângulos e suas medidas|Angles and their measures|角|角與角度
Translação e simetria|Translation and symmetry|平移|平移與對稱
Medição de massa|Measuring mass|质量|質量測量
Gráficos de barras|Bar charts|条形统计图|長條統計圖
Média aritmética|Arithmetic mean|平均数|算術平均

CN|matematica|5-6|Proporção e dados
Fatores e múltiplos|Factors and multiples|因数|因數與倍數
Divisibilidade e números primos|Divisibility and prime numbers|质数|整除與質數
Decimais nas quatro operações|Four operations with decimals|小数四则|小數四則運算
Frações nas quatro operações|Four operations with fractions|分数四则|分數四則運算
Razão e percentagem|Ratio and percentage|百分数|比與百分數
Relações proporcionais|Proportional relationships|比例|比例關係
Expressões simples com letras|Simple literal expressions|字母|簡單字母式
Equações simples|Simple equations|方程|簡單方程
Área de triângulos e paralelogramos|Area of triangles and parallelograms|三角形|三角形與平行四邊形面積
Área e perímetro do círculo|Circle area and circumference|圆|圓面積與圓周
Volume de prismas e cilindros|Volumes of prisms and cylinders|体积|角柱與圓柱體積
Gráficos de setores|Pie charts|扇形统计图|扇形統計圖
Possibilidade e incerteza|Possibility and uncertainty|可能性|可能性與不確定性
Planeamento de investigações|Planning investigations|调查|規劃調查

CN|matematica|7-9|Álgebra, geometria e estatística
Números racionais|Rational numbers|有理数|有理數
Números reais|Real numbers|实数|實數
Radicais e potências|Radicals and powers|平方根|根式與冪
Polinómios|Polynomials|整式|多項式
Fatoração algébrica|Algebraic factorisation|因式分解|因式分解
Expressões racionais|Rational expressions|分式|分式
Equações lineares|Linear equations|一元一次方程|一元一次方程
Sistemas de equações|Simultaneous equations|二元一次方程组|二元一次聯立方程
Inequações lineares|Linear inequalities|一元一次不等式|一元一次不等式
Equações quadráticas|Quadratic equations|一元二次方程|一元二次方程
Funções afins|Linear functions|一次函数|一次函數
Funções quadráticas|Quadratic functions|二次函数|二次函數
Função de proporcionalidade inversa|Inverse proportion function|反比例函数|反比例函數
Triângulos congruentes|Congruent triangles|全等|全等三角形
Semelhança geométrica|Geometric similarity|相似|圖形相似
Teorema de Pitágoras|Pythagorean theorem|勾股定理|畢氏定理
Propriedades dos círculos|Properties of circles|圆|圓的性質
Trigonometria no triângulo retângulo|Right-triangle trigonometry|三角函数|直角三角形三角比
Estatística descritiva|Descriptive statistics|统计|敘述統計
Probabilidade de eventos|Probability of events|概率|事件機率

CN|chines|1-2|Língua chinesa inicial
Sons do mandarim e pinyin|Mandarin sounds and pinyin|汉语拼音|漢語語音與拼音
Traços e escrita de caracteres|Character strokes and writing|笔画|漢字筆畫與書寫
Radicais dos caracteres|Character components|偏旁|漢字部件與偏旁
Reconhecimento de caracteres|Character recognition|识字|識字
Escrita regular de caracteres|Regular character handwriting|写字|漢字規範書寫
Leitura oral de textos|Reading texts aloud|朗读|文章朗讀
Escuta e comunicação oral|Listening and oral communication|口语交际|聆聽與口語交際
Leitura prazerosa|Reading for pleasure|阅读|閱讀興趣

CN|chines|3-4|Leitura, escrita e expressão
Uso do dicionário chinês|Using Chinese dictionaries|字典|使用中文字典
Vocabulário em contexto|Vocabulary in context|词语|語境中的詞語
Leitura fluente|Fluent reading|朗读|流暢朗讀
Ideia principal e parágrafos|Main ideas and paragraphs|主要内容|主旨與段落
Relato de acontecimentos|Recounting events|叙述|敘述事件
Escrita de observações|Writing observations|观察|觀察記錄
Comunicação com clareza|Clear communication|表达|清楚表達
Leitura de poesia|Reading poetry|诗文|閱讀詩文

CN|chines|5-6|Compreensão e produção textual
Comparação de textos|Comparing texts|阅读|比較文本
Inferência e compreensão|Inference and comprehension|理解|推論與理解
Factos, opiniões e evidências|Facts opinions and evidence|表达|事實意見與證據
Planeamento de composições|Planning compositions|习作|作文規劃
Revisão da própria escrita|Revising one's writing|修改|修改自己的文章
Pesquisa e síntese|Research and synthesis|资料|資料蒐集與整理
Herança literária chinesa|Chinese literary heritage|传统文化|中華文學傳承
Apresentação oral organizada|Organised oral presentations|口语交际|有條理的口頭報告

CN|chines|7-9|Língua e literatura do secundário inferior
Leitura crítica e argumentação|Critical reading and argumentation|思辨|批判閱讀與論證
Estrutura de textos argumentativos|Argumentative text structure|议论|議論文結構
Narrador e construção literária|Narrator and literary construction|文学|敘述者與文學結構
Recursos expressivos e linguagem|Expressive language devices|语言|語言表現手法
Chinês clássico introdutório|Introduction to classical Chinese|文言|文言文入門
Poesia e tradição cultural|Poetry and cultural tradition|诗歌|詩歌與文化傳統
Pesquisa temática com fontes|Source-based thematic inquiry|专题|以資料為本的專題探究
Revisão e apresentação de textos|Revising and presenting texts|写作|文章修訂與發表

CN|ciencias|1-2|Exploração científica inicial
Sentidos e observação|Senses and observation|观察|感官與觀察
Propriedades observáveis dos materiais|Observable material properties|物体|物體的可觀察性質
Classificação de objetos|Classifying objects|分类|物件分類
Partes externas das plantas|External parts of plants|植物|植物的外部構造
Animais e suas necessidades|Animals and their needs|动物|動物與生存需要
Água no cotidiano|Water in daily life|水|日常生活中的水
Ar e movimento|Air and movement|空气|空氣與運動
Sol e sombras|Sun and shadows|太阳|太陽與影子
Registo do tempo atmosférico|Recording weather|天气|記錄天氣
Construção e teste de modelos|Building and testing models|模型|建造與測試模型

CN|ciencias|3-4|Materiais, energia e vida
Estados físicos e materiais|States of matter and materials|物质|物態與材料
Dissolução e misturas|Dissolving and mixtures|溶解|溶解與混合物
Forças e movimento|Forces and motion|力|力與運動
Som e vibração|Sound and vibration|声音|聲音與振動
Luz e propagação|Light and propagation|光|光及其傳播
Eletricidade e circuitos|Electricity and circuits|电|電與電路
Ímanes e magnetismo|Magnets and magnetism|磁|磁鐵與磁性
Desenvolvimento dos seres vivos|Development of organisms|生长|生物的生長發育
Rochas e solo|Rocks and soil|岩石|岩石與土壤
Ciclo da água|Water cycle|水循环|水循環

CN|ciencias|5-6|Sistemas naturais e investigação
Conservação da matéria|Conservation of matter|物质|物質守恆
Calor e temperatura|Heat and temperature|热|熱與溫度
Transformação de energia|Energy transformation|能量|能量轉換
Movimento e mecanismos|Motion and mechanisms|机械|運動與機械
Estruturas e estabilidade|Structures and stability|结构|結構與穩定
Corpo humano e saúde|Human body and health|人体|人體與健康
Relações ecológicas|Ecological relationships|环境|生態關係
Hereditariedade introdutória|Introduction to heredity|遗传|遺傳入門
Terra e Sistema Solar|Earth and the Solar system|地球|地球與太陽系
Evidências e investigação científica|Evidence and scientific inquiry|证据|證據與科學探究

CN|historia|7-9|História chinesa e mundial
Primeiras sociedades humanas|Early human societies|人类|早期人類社會
Origens da civilização chinesa|Origins of Chinese civilisation|文明|中華文明的起源
China antiga e dinastias|Ancient China and dynasties|夏商周|中國古代與王朝
Unificação Qin e governo Han|Qin unification and Han government|秦汉|秦統一與漢朝制度
Contactos pelas rotas da seda|Silk Road contacts|丝绸之路|絲綢之路的交流
Sociedade Tang e Song|Tang and Song society|隋唐|唐宋社會
China Yuan, Ming e Qing|Yuan Ming and Qing China|明清|元明清時期的中國
Intercâmbios culturais e tecnológicos|Cultural and technological exchanges|交流|文化與技術交流
China no século XIX|China in the nineteenth century|鸦片战争|十九世紀的中國
Revoluções e transformação social|Revolutions and social transformation|革命|革命與社會變遷
Guerras mundiais e século XX|World wars and the twentieth century|世界大战|世界大戰與二十世紀
Fundação da República Popular da China|Founding of the People's Republic of China|中华人民共和国|中華人民共和國的成立
Reforma e abertura na China|Reform and opening in China|改革开放|中國的改革開放
Civilizações do mundo antigo|Civilisations of the ancient world|古代文明|世界古代文明
Renascimento e expansão marítima|Renaissance and maritime expansion|文艺复兴|文藝復興與海上擴張
Revolução Industrial|Industrial Revolution|工业革命|工業革命
Fontes e cronologia histórica|Historical sources and chronology|史料|史料與年代

CN|geografia|7-9|Geografia chinesa e mundial
Globo e coordenadas geográficas|Globe and geographic coordinates|地球仪|地球儀與地理座標
Mapas e escala|Maps and scale|地图|地圖與比例尺
Continentes e oceanos|Continents and oceans|海洋|大洲與海洋
Relevo e processos terrestres|Relief and Earth processes|地形|地形與地表作用
Tempo e clima|Weather and climate|气候|天氣與氣候
População e assentamentos|Population and settlement|人口|人口與聚落
Diversidade cultural mundial|World cultural diversity|文化|世界文化多樣性
Recursos naturais e sustentabilidade|Natural resources and sustainability|资源|自然資源與永續發展
Território e população da China|Chinese territory and population|中国|中國領土與人口
Grandes rios chineses|Major Chinese rivers|河流|中國主要河流
Regiões naturais da China|Natural regions of China|区域|中國自然地區
Agricultura e indústria chinesas|Chinese agriculture and industry|产业|中國農業與工業
Interdependência mundial|Global interdependence|全球|全球相互依存
Investigação com dados geográficos|Geographic data inquiry|地理信息|地理資訊探究

CN|computacao|1-2|Informação no cotidiano
Informação e sentidos|Information and senses|信息|資訊與感官
Dispositivos digitais cotidianos|Everyday digital devices|数字设备|日常數碼設備
Identidade e proteção de dados|Identity and data protection|保护|身分與資料保護
Regras de utilização dos dispositivos|Device-use rules|规则|設備使用規則
Descrição de sequências|Describing sequences|步骤|描述步驟順序
Representações de informação|Representations of information|表达|資訊的表示

CN|computacao|3-4|Dados e algoritmos iniciais
Codificação de informação|Encoding information|编码|資訊編碼
Organização e armazenamento de dados|Organising and storing data|存储|資料整理與儲存
Pesquisa de informação digital|Finding digital information|检索|檢索數碼資訊
Algoritmos do cotidiano|Everyday algorithms|算法|日常演算法
Divisão de problemas em passos|Breaking problems into steps|分解|將問題分解為步驟
Comunicação e colaboração digital|Digital communication and collaboration|交流|數碼溝通與協作

CN|computacao|5-6|Redes e pensamento computacional
Organização de redes|Network organisation|网络|網絡組織
Publicação e partilha responsável|Responsible publishing and sharing|共享|負責任的發布與共享
Dados e resolução de problemas|Data and problem solving|数据|資料與問題解決
Estruturas de controlo de programas|Program control structures|控制|程式控制結構
Processos e controlo de sistemas|Processes and system control|过程|系統流程與控制
Avaliação crítica de informação|Critical information evaluation|评价|資訊的批判評估

CN|computacao|7-9|Computação do secundário inferior
Internet e aplicações|Internet and applications|互联网|互聯網及其應用
Sistemas físicos e digitais|Physical and digital systems|物联网|物理與數碼系統
Inteligência artificial introdutória|Introduction to artificial intelligence|人工智能|人工智能入門
Segurança e riscos digitais|Digital security and risks|安全|數碼安全與風險
Modelação com dados|Data modelling|数据|資料建模
Projeto e programação de soluções|Designing and programming solutions|程序|方案設計與程式編寫

CN|educacao-moral|1-2|Convivência e responsabilidade inicial
Conhecimento de si|Knowing oneself|自我|認識自己
Relações com a família|Family relationships|家庭|家庭關係
Cooperação e vida escolar|Cooperation and school life|学校|合作與學校生活
Cuidado com outras pessoas|Caring for others|关心|關心他人
Regras na convivência|Rules for living together|规则|共同生活的規則

CN|educacao-moral|3-6|Vida em comunidade
Responsabilidades na comunidade|Community responsibilities|责任|社區責任
Honestidade nas relações|Honesty in relationships|诚信|人際交往中的誠信
Respeito pela diversidade|Respect for diversity|尊重|尊重多樣性
Património e identidade cultural|Heritage and cultural identity|文化|文化傳承與認同
Proteção de crianças|Protecting children|保护|兒童保護
Consumo e vida coletiva|Consumption and collective life|生活|消費與共同生活
Consciência ambiental|Environmental awareness|环境|環境意識
Introdução às leis|Introduction to laws|法律|法律入門

CN|educacao-moral|7-9|Cidadania, instituições e direito
Direitos e deveres|Rights and duties|权利|權利與義務
Constituição chinesa e instituições|Chinese constitution and institutions|宪法|中國憲法與制度
Participação e responsabilidade social|Participation and social responsibility|社会|參與及社會責任
Regras jurídicas e vida cotidiana|Law and daily life|法治|法治與日常生活
Identidade cultural e relações internacionais|Cultural identity and international relations|国家|文化認同與國際關係

CN|trabalho-pratico|1-2|Práticas de vida cotidiana
Organização de objetos pessoais|Organising personal belongings|整理|整理個人物品
Limpeza de espaços cotidianos|Cleaning everyday spaces|清洁|清潔日常空間
Cuidados simples com roupas|Simple clothing care|衣物|簡單衣物照護
Preparação simples de alimentos|Simple food preparation|烹饪|簡單食物準備
Cultivo e cuidado de plantas|Growing and caring for plants|种植|植物栽培與照護

CN|trabalho-pratico|3-4|Trabalho, materiais e cooperação
Uso seguro de ferramentas|Safe tool use|工具|安全使用工具
Trabalhos manuais|Handcrafts|手工|手工製作
Conservação de materiais|Caring for materials|材料|材料保養
Cooperação em tarefas domésticas|Cooperating in household tasks|家务|合作完成家務
Cultivo e cuidados com animais|Cultivation and animal care|养殖|種養與動物照護

CN|trabalho-pratico|5-6|Produção e serviço
Planeamento de tarefas|Planning tasks|计划|工作規劃
Alimentação e conservação de alimentos|Food and food storage|食品|食物與食品保存
Manutenção de utensílios|Maintaining utensils|维护|器具維護
Experiências de produção agrícola|Agricultural production experiences|农业|農業生產體驗
Serviço à comunidade|Community service|服务|社區服務

CN|trabalho-pratico|7-9|Projetos de trabalho
Projeto e produção de objetos|Designing and producing objects|制作|物品設計與製作
Organização de processos produtivos|Organising production processes|生产|生產流程組織
Tecnologias de produção|Production technologies|技术|生產技術
Trabalho e ambiente|Work and environment|环境|勞動與環境
Ética e valorização do trabalho|Work ethics and appreciation|劳动|勞動倫理與價值

CN|ciencias|7-9|Física do secundário inferior
Movimento e medição|Motion and measurement|运动|運動與測量
Forças e interação|Forces and interaction|相互作用|力與相互作用
Pressão e flutuação|Pressure and buoyancy|压强|壓力與浮力
Trabalho e energia|Work and energy|功|功與能量
Temperatura e calor|Temperature and heat|温度|溫度與熱
Som e fenómenos acústicos|Sound phenomena|声|聲音現象
Luz e formação de imagens|Light and image formation|光|光與成像
Corrente e tensão|Current and voltage|电流|電流與電壓
Circuitos e resistência|Circuits and resistance|电路|電路與電阻
Magnetismo e indução|Magnetism and induction|磁|磁性與感應

CN|ciencias|7-9|Química do secundário inferior
Materiais e substâncias|Materials and substances|物质|材料與物質
Átomos e moléculas|Atoms and molecules|分子|原子與分子
Elementos e compostos|Elements and compounds|元素|元素與化合物
Tabela periódica introdutória|Introduction to the periodic table|周期表|元素週期表入門
Reações químicas|Chemical reactions|化学反应|化學反應
Conservação da massa|Conservation of mass|质量守恒|質量守恆
Oxigénio e combustão|Oxygen and combustion|氧气|氧氣與燃燒
Água e soluções|Water and solutions|溶液|水與溶液
Ácidos, bases e sais|Acids bases and salts|酸|酸鹼鹽
Química e sustentabilidade|Chemistry and sustainability|资源|化學與永續發展

CN|ciencias|7-9|Biologia do secundário inferior
Célula e organização dos seres vivos|Cells and organisation of life|细胞|細胞與生命組織
Tecidos e órgãos|Tissues and organs|组织|組織與器官
Nutrição dos organismos|Nutrition in organisms|营养|生物營養
Fotossíntese e respiração|Photosynthesis and respiration|光合作用|光合作用與呼吸
Reprodução de plantas e animais|Plant and animal reproduction|生殖|植物與動物生殖
Hereditariedade e variação|Heredity and variation|遗传|遺傳與變異
Classificação e diversidade biológica|Classification and biodiversity|多样性|分類與生物多樣性
Ecossistemas e fluxos de energia|Ecosystems and energy flows|生态系统|生態系與能量流動
Equilíbrio e conservação|Balance and conservation|保护|生態平衡與保育
Evolução biológica introdutória|Introduction to evolution|进化|生物演化入門

CN|arte|1-2|Exploração artística inicial
Ritmo e canto|Rhythm and singing|唱游|節奏與歌唱
Escuta e apreciação sonora|Listening and sound appreciation|音乐|聆聽與聲音欣賞
Desenho e cores|Drawing and colours|造型|繪畫與色彩
Movimento e dança|Movement and dance|舞蹈|動作與舞蹈
Imaginação e expressão|Imagination and expression|表现|想像與表現

CN|arte|3-6|Práticas e culturas artísticas
Melodia e criação musical|Melody and musical creation|音乐|旋律與音樂創作
Instrumentos e timbres|Instruments and timbre|器乐|樂器與音色
Criação visual com materiais|Visual creation with materials|美术|材料與視覺創作
Narrativas cênicas|Stage narratives|戏剧|舞台敘事
Artes e património cultural|Arts and cultural heritage|文化|藝術與文化資產
Imagem e meios digitais|Images and digital media|媒体|圖像與數碼媒體

CN|arte|7-9|Artes do secundário inferior
Análise de obras artísticas|Analysing works of art|鉴赏|藝術作品分析
Projeto artístico autoral|Personal artistic projects|创作|個人藝術專題
Música, sociedade e cultura|Music society and culture|音乐|音樂社會與文化
Teatro, cinema e representação|Theatre film and representation|影视|戲劇電影與表演
Integração de linguagens artísticas|Integrating artistic languages|综合|藝術語言整合

CN|educacao-fisica|1-2|Movimento e atividade física inicial
Movimentos locomotores|Locomotor movements|移动|移動技能
Equilíbrio e coordenação|Balance and coordination|平衡|平衡與協調
Jogos motores cooperativos|Cooperative movement games|游戏|合作性動作遊戲
Manipulação de objetos|Object manipulation|操控|操控物件
Segurança e hábitos de higiene|Safety and hygiene habits|卫生|安全與衛生習慣

CN|educacao-fisica|3-6|Práticas corporais e saúde
Corridas e saltos|Running and jumping|田径|跑與跳
Jogos e desportos com bola|Ball games and sports|球类|球類遊戲與運動
Ginástica e controlo corporal|Gymnastics and body control|体操|體操與身體控制
Atividades aquáticas|Aquatic activities|水上|水上活動
Condição física e exercício|Physical fitness and exercise|体能|體能與鍛鍊
Nutrição e atividade física|Nutrition and physical activity|营养|營養與身體活動

CN|educacao-fisica|7-9|Educação física do secundário inferior
Planeamento de atividade física|Planning physical activity|锻炼|身體活動規劃
Técnicas e táticas desportivas|Sport techniques and tactics|战术|運動技術與戰術
Práticas tradicionais chinesas|Traditional Chinese physical practices|中华传统|中華傳統體育
Cooperação e regras desportivas|Cooperation and sport rules|规则|合作與運動規則
Prevenção de lesões no desporto|Preventing sports injuries|损伤|預防運動傷害

JP|vida-cotidiana|1-2|Vida cotidiana e ambiente
Conhecer a escola e as pessoas|Knowing the school and its people|学校|認識學校與人們
Cooperação com a família|Family cooperation|家庭|與家人合作
Exploração do bairro|Exploring the neighbourhood|地域|探索社區
Segurança nos espaços públicos|Safety in public spaces|公共|公共場所安全
Animais e plantas próximos|Nearby animals and plants|動植物|身邊的動植物
Mudanças das estações|Seasonal changes|季節|季節變化
Brinquedos e materiais do cotidiano|Toys and everyday materials|遊び|玩具與日常材料
Comunicação com outras pessoas|Communicating with others|伝え合|與他人溝通
Crescimento e autonomia pessoal|Growth and personal independence|成長|成長與個人自主

JP|ingles|7-9|Comunicação no secundário inferior
Escuta de ideias principais|Listening for main ideas|聞くこと|聆聽主旨
Leitura de informações específicas|Reading for specific information|読むこと|閱讀特定資訊
Conversação e troca de informações|Conversation and information exchange|やり取り|對話與資訊交流
Apresentações orais|Oral presentations|発表|口頭報告
Produção de textos em inglês|Writing English texts|書くこと|英語文章寫作
Sons e entoação do inglês|English sounds and intonation|イントネーション|英語語音與語調
Estruturas gramaticais em contexto|Grammar structures in context|文法|語境中的文法結構
Vocabulário e comunicação intercultural|Vocabulary and intercultural communication|文化|詞彙與跨文化溝通

JP|arte|7-9|Artes do secundário inferior
Expressão vocal e instrumental|Vocal and instrumental expression|器楽|聲樂與器樂表現
Criação e apreciação musical|Musical creation and appreciation|創作|音樂創作與欣賞
Músicas japonesas e do mundo|Music from Japan and the world|我が国|日本與世界音樂
Desenho e pintura expressiva|Expressive drawing and painting|絵や彫刻|表現性繪畫
Escultura e expressão espacial|Sculpture and spatial expression|彫刻|雕塑與空間表現
Design e comunicação visual|Design and visual communication|デザイン|設計與視覺溝通
Patrimônio artístico e cultural|Artistic and cultural heritage|文化|藝術與文化資產

JP|educacao-fisica|7-9|Movimento e saúde no secundário inferior
Desenvolvimento da condição física|Developing physical fitness|体力|發展體能
Atletismo e desempenho motor|Athletics and motor performance|陸上競技|田徑與動作表現
Natação e segurança aquática|Swimming and water safety|水泳|游泳與水域安全
Jogos de invasão e cooperação|Invasion games and cooperation|球技|侵入類球賽與合作
Práticas tradicionais de budō|Traditional budo practices|武道|傳統武道
Dança e expressão corporal|Dance and bodily expression|ダンス|舞蹈與身體表現
Hábitos de vida e prevenção|Lifestyle habits and prevention|生活習慣|生活習慣與預防

JP|educacao-moral|7-9|Educação moral do secundário inferior
Autonomia e responsabilidade pessoal|Autonomy and personal responsibility|自律|自主與個人責任
Compreensão e tolerância|Understanding and tolerance|寛容|理解與寬容
Justiça e equidade|Justice and fairness|公正|公正與公平
Participação e bem coletivo|Participation and collective wellbeing|公共|參與與公共福祉
Respeito pela vida e pela natureza|Respect for life and nature|生命|尊重生命與自然
Compreensão internacional|International understanding|国際理解|國際理解

JP|economia-domestica|7-9|Vida doméstica no secundário inferior
Desenvolvimento e cuidado de crianças|Child development and care|幼児|兒童發展與照護
Planejamento de refeições|Planning meals|献立|膳食規劃
Preparação e conservação de alimentos|Food preparation and storage|食品|食物準備與保存
Materiais e cuidados com roupas|Clothing materials and care|衣服|衣物材料與照護
Habitação e segurança doméstica|Housing and home safety|住居|住宅與家居安全
Decisões de consumo responsável|Responsible consumer decisions|消費|負責任的消費決定

CN|ingles|3-4|Comunicação inicial em inglês
Sons e palavras familiares|Familiar sounds and words|语音|熟悉的語音與詞語
Cumprimentos e apresentação pessoal|Greetings and introductions|交流|問候與自我介紹
Vocabulário sobre pessoas e objetos|Vocabulary about people and objects|词汇|人物與物品詞彙
Escuta de informações simples|Listening to simple information|听|聆聽簡單資訊
Perguntas e respostas breves|Short questions and answers|表达|簡短問答
Leitura de palavras e frases simples|Reading simple words and sentences|阅读|閱讀簡單詞句
Escrita de palavras conhecidas|Writing familiar words|书写|書寫熟悉詞語
Canções e histórias em inglês|Songs and stories in English|故事|英語歌曲與故事

CN|ingles|5-6|Interação e compreensão em inglês
Compreensão de diálogos cotidianos|Understanding everyday dialogues|理解|理解日常對話
Relato de experiências pessoais|Recounting personal experiences|表达|敘述個人經驗
Vocabulário temático em contexto|Thematic vocabulary in context|词汇|語境中的主題詞彙
Estruturas gramaticais básicas|Basic grammar structures|语法|基本文法結構
Leitura de textos curtos|Reading short texts|语篇|閱讀短文
Produção de mensagens breves|Writing short messages|写|撰寫簡短訊息
Estratégias de aprendizagem de línguas|Language learning strategies|策略|語言學習策略
Semelhanças e diferenças culturais|Cultural similarities and differences|文化|文化的異同

CN|ingles|7-9|Inglês do secundário inferior
Compreensão global de textos|Overall text comprehension|理解|文本整體理解
Inferência com pistas linguísticas|Inference from language clues|语言|以語言線索推論
Interação oral sustentada|Sustained oral interaction|交流|持續口語互動
Exposição de opiniões e argumentos|Expressing opinions and arguments|观点|表達意見與論點
Escrita de narrativas e relatos|Writing narratives and reports|语篇|敘事與報告寫作
Revisão da produção em inglês|Revising English writing|评价|修訂英語寫作
Consciência intercultural|Intercultural awareness|文化意识|跨文化意識
Pesquisa e aprendizagem autônoma|Research and independent learning|学习能力|探究與自主學習
"""
