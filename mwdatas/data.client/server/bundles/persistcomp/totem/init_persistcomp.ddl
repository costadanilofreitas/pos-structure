BEGIN TRANSACTION;
-- init l10n categories
insert or replace into totemdb.locale values ('pt-br', 'CAT_FEATURED', 'Destaques');
insert or replace into totemdb.locale values ('pt-br', 'CAT_FEATURED_URL', '/totem/images/categories/featured.png');

insert or replace into totemdb.locale values ('pt-br', 'CAT_MEAT_BURGER', 'Hambúrgueres de Carne');
insert or replace into totemdb.locale values ('pt-br', 'CAT_MEAT_BURGER_URL', '/totem/images/categories/meat.png');

insert or replace into totemdb.locale values ('pt-br', 'CAT_HOT_DOG', 'Cachorro Quente');
insert or replace into totemdb.locale values ('pt-br', 'CAT_HOT_DOG_URL', '/totem/images/categories/hotdog.png');

insert or replace into totemdb.locale values ('pt-br', 'CAT_CHICKEN', 'Hambúrgueres de Frango');
insert or replace into totemdb.locale values ('pt-br', 'CAT_CHICKEN_URL', '/totem/images/categories/chicken.png');

insert or replace into totemdb.locale values ('pt-br', 'CAT_SALAD', 'Saladas e Vegetariano');
insert or replace into totemdb.locale values ('pt-br', 'CAT_SALAD_URL', '/totem/images/categories/salad.png');

insert or replace into totemdb.locale values ('pt-br', 'CAT_DRINKS', 'Bebidas');
insert or replace into totemdb.locale values ('pt-br', 'CAT_DRINKS_URL', '/totem/images/categories/drinks.png');

insert or replace into totemdb.locale values ('pt-br', 'CAT_SIDES', 'Acompanhamentos');
insert or replace into totemdb.locale values ('pt-br', 'CAT_SIDES_URL', '/totem/images/categories/sides.png');

insert or replace into totemdb.locale values ('pt-br', 'CAT_DESSERTS', 'Sobremesas');
insert or replace into totemdb.locale values ('pt-br', 'CAT_DESSERTS_URL', '/totem/images/categories/desserts.png');

insert or replace into totemdb.locale values ('pt-br', 'CAT_KIDS', 'Kids');
insert or replace into totemdb.locale values ('pt-br', 'CAT_KIDS_URL', '/totem/images/categories/kids.png');

insert or replace into totemdb.locale values ('pt-br', 'CAT_PROMO', 'Promoções');
insert or replace into totemdb.locale values ('pt-br', 'CAT_PROMO_URL', '/totem/images/categories/promo.png');

-- init categories
insert or replace into totemdb.category values (99, 'Promoções', 1, '#F0AB00', 'CAT_PROMO', 'CAT_PROMO_URL');
insert or replace into totemdb.category values (2, 'Destaques', 1, '#8F542D', 'CAT_FEATURED', 'CAT_FEATURED_URL');
insert or replace into totemdb.category values (3, 'Hambúrgueres de Carne', 1, '#84332E', 'CAT_MEAT_BURGER', 'CAT_MEAT_BURGER_URL');
insert or replace into totemdb.category values (4, 'Cachorro Quente', 1, '#ED7800', 'CAT_HOT_DOG', 'CAT_HOT_DOG_URL');
insert or replace into totemdb.category values (5, 'Hambúrgueres de Frango', 1, '#59980D', 'CAT_CHICKEN', 'CAT_CHICKEN_URL');
insert or replace into totemdb.category values (6, 'Saladas e Vegetariano', 1, '#A2007D', 'CAT_SALAD', 'CAT_SALAD_URL');
insert or replace into totemdb.category values (7, 'Bebidas', 1, '#F6A800', 'CAT_DRINKS', 'CAT_DRINKS_URL');
insert or replace into totemdb.category values (8, 'Acompanhamentos', 1, '#0071CE', 'CAT_SIDES', 'CAT_SIDES_URL');
insert or replace into totemdb.category values (9, 'Sobremesas', 1, '#9063CD', 'CAT_DESSERTS', 'CAT_DESSERTS_URL');
insert or replace into totemdb.category values (10, 'Kids', 1, '#E41613', 'CAT_KIDS', 'CAT_KIDS_URL');

-- init categoryProduct
-- Destaques
insert or replace into totemdb.categoryProduct values (2, 1050);
insert or replace into totemdb.categoryProduct values (2, 7100023);

-- hamburgueres de carne
insert or replace into totemdb.categoryProduct values (3, 7100054); -- costela furiosa
insert or replace into totemdb.categoryProduct values (3, 7100053); -- costela bbq bacon
insert or replace into totemdb.categoryProduct values (3, 7100003); -- picanha churras
insert or replace into totemdb.categoryProduct values (3, 7100051); -- picanha chimichurras
insert or replace into totemdb.categoryProduct values (3, 7100036); -- rodeio
insert or replace into totemdb.categoryProduct values (3, 2610); -- mega stacker 2.0
insert or replace into totemdb.categoryProduct values (3, 2612); -- mega stacker 3.0
insert or replace into totemdb.categoryProduct values (3, 2614); -- mega stacker 4.0
insert or replace into totemdb.categoryProduct values (3, 1050); -- whopper
insert or replace into totemdb.categoryProduct values (3, 1052); -- whopper duplo
insert or replace into totemdb.categoryProduct values (3, 1600); -- whopper jr
insert or replace into totemdb.categoryProduct values (3, 1700); -- whopper furioso
insert or replace into totemdb.categoryProduct values (3, 2604); -- stacker triplo
insert or replace into totemdb.categoryProduct values (3, 5000074); -- picanha
insert or replace into totemdb.categoryProduct values (3, 5000413); -- picanha bbq bacon
insert or replace into totemdb.categoryProduct values (3, 7100023); -- big king
insert or replace into totemdb.categoryProduct values (3, 1804); -- cheddar duplo
insert or replace into totemdb.categoryProduct values (3, 2106); -- x burg duplo bacon
insert or replace into totemdb.categoryProduct values (3, 7100021); -- x burg bacon
insert or replace into totemdb.categoryProduct values (3, 2100); -- x burg
insert or replace into totemdb.categoryProduct values (3, 2050); -- hamburg

-- cachorro quente
insert or replace into totemdb.categoryProduct values (4, 7100048);
insert or replace into totemdb.categoryProduct values (4, 7100049);

-- hamburgueres de frango
insert or replace into totemdb.categoryProduct values (5, 3100);
insert or replace into totemdb.categoryProduct values (5, 2700);
insert or replace into totemdb.categoryProduct values (5, 2064);

-- saladas
insert or replace into totemdb.categoryProduct values (6, 7100033);
insert or replace into totemdb.categoryProduct values (6, 7800001);

-- bebidas
insert or replace into totemdb.categoryProduct values (7, 9008);
insert or replace into totemdb.categoryProduct values (7, 7500003);

insert or replace into totemdb.categoryProduct values (7, 9052);
insert or replace into totemdb.categoryProduct values (7, 9053);
insert or replace into totemdb.categoryProduct values (7, 9054);
insert or replace into totemdb.categoryProduct values (7, 9103);
insert or replace into totemdb.categoryProduct values (7, 9104);
insert or replace into totemdb.categoryProduct values (7, 9101);
insert or replace into totemdb.categoryProduct values (7, 9102);
insert or replace into totemdb.categoryProduct values (7, 9105);
insert or replace into totemdb.categoryProduct values (7, 9106);
insert or replace into totemdb.categoryProduct values (7, 9107);

-- acompanhamentos
insert or replace into totemdb.categoryProduct values (8, 6011);
insert or replace into totemdb.categoryProduct values (8, 6012);
insert or replace into totemdb.categoryProduct values (8, 6013);
insert or replace into totemdb.categoryProduct values (8, 6020);
insert or replace into totemdb.categoryProduct values (8, 6019);
insert or replace into totemdb.categoryProduct values (8, 6025);
insert or replace into totemdb.categoryProduct values (8, 6027);
insert or replace into totemdb.categoryProduct values (8, 6021);
insert or replace into totemdb.categoryProduct values (8, 6028);
insert or replace into totemdb.categoryProduct values (8, 7300002);
insert or replace into totemdb.categoryProduct values (8, 7300005);
insert or replace into totemdb.categoryProduct values (8, 6017);
insert or replace into totemdb.categoryProduct values (8, 6018);
insert or replace into totemdb.categoryProduct values (8, 6508);
insert or replace into totemdb.categoryProduct values (8, 6522);
insert or replace into totemdb.categoryProduct values (8, 7300001);
insert or replace into totemdb.categoryProduct values (8, 7300014);

-- sobremesas
insert or replace into totemdb.categoryProduct values (9, 20000);
insert or replace into totemdb.categoryProduct values (9, 20001);
insert or replace into totemdb.categoryProduct values (9, 20002);
insert or replace into totemdb.categoryProduct values (9, 8000001);
insert or replace into totemdb.categoryProduct values (9, 8000006);
insert or replace into totemdb.categoryProduct values (9, 8000007);
insert or replace into totemdb.categoryProduct values (9, 8000008);
insert or replace into totemdb.categoryProduct values (9, 8000012);
insert or replace into totemdb.categoryProduct values (9, 5000278);
insert or replace into totemdb.categoryProduct values (9, 5000420);
insert or replace into totemdb.categoryProduct values (9, 6000072);
insert or replace into totemdb.categoryProduct values (9, 20006);
insert or replace into totemdb.categoryProduct values (9, 20007);
insert or replace into totemdb.categoryProduct values (9, 20008);
insert or replace into totemdb.categoryProduct values (9, 8000013);
insert or replace into totemdb.categoryProduct values (9, 8000025);
insert or replace into totemdb.categoryProduct values (9, 20009);
insert or replace into totemdb.categoryProduct values (9, 20010);
insert or replace into totemdb.categoryProduct values (9, 20011);
insert or replace into totemdb.categoryProduct values (9, 20026);
insert or replace into totemdb.categoryProduct values (9, 20029);
insert or replace into totemdb.categoryProduct values (9, 20027);

-- kids
insert or replace into totemdb.categoryProduct values (10, 7100012);
insert or replace into totemdb.categoryProduct values (10, 6501);
insert or replace into totemdb.categoryProduct values (10, 6503);
insert or replace into totemdb.categoryProduct values (10, 6509);
insert or replace into totemdb.categoryProduct values (10, 7900001);

-- init products locale

-- hamburgeres de carne
insert or replace into totemdb.locale values ('pt-br', '7100054', 'BK™ Costela Furiosa');
insert or replace into totemdb.locale values ('pt-br', '7100054_URL', '/totem/images/products/7100054.png');
insert or replace into totemdb.locale values ('pt-br', '6000605', 'Combo BK™ Costela Furiosa');
-- insert or replace into totemdb.locale values ('pt-br', '6000605_URL', '/totem/images/products/6000605.png');

insert or replace into totemdb.locale values ('pt-br', '7100053', 'BK™ Costela Barbecue Bacon');
insert or replace into totemdb.locale values ('pt-br', '7100053_URL', '/totem/images/products/7100053.png');
insert or replace into totemdb.locale values ('pt-br', '6000604', 'Combo BK™ Costela Barbecue Bacon');
-- insert or replace into totemdb.locale values ('pt-br', '6000604_URL', '/totem/images/products/6000604.png');

insert or replace into totemdb.locale values ('pt-br', '7100003', 'Picanha Churras');
insert or replace into totemdb.locale values ('pt-br', '7100003_URL', '/totem/images/products/7100003.png');
insert or replace into totemdb.locale values ('pt-br', '7100002', 'Combo Picanha Churras');
-- insert or replace into totemdb.locale values ('pt-br', '7100002_URL', '/totem/images/products/7100002.png');

insert or replace into totemdb.locale values ('pt-br', '7100051', 'Picanha Chimichurras');
insert or replace into totemdb.locale values ('pt-br', '7100051_URL', '/totem/images/products/7100051.png');
insert or replace into totemdb.locale values ('pt-br', '7000019', 'Combo Picanha Chimichurras');
-- insert or replace into totemdb.locale values ('pt-br', '7000019_URL', '/totem/images/products/7000019.png');

insert or replace into totemdb.locale values ('pt-br', '7100036', 'Rodeio Burger');
insert or replace into totemdb.locale values ('pt-br', '7100036_URL', '/totem/images/products/7100036.png');
insert or replace into totemdb.locale values ('pt-br', '7000007', 'Combo Rodeio Burger');
-- insert or replace into totemdb.locale values ('pt-br', '7000007_URL', '/totem/images/products/7000007.png');

insert or replace into totemdb.locale values ('pt-br', '2610', 'Mega Stacker 2.0');
insert or replace into totemdb.locale values ('pt-br', '2610_URL', '/totem/images/products/2610.png');
insert or replace into totemdb.locale values ('pt-br', '2611', 'Combo Mega Stacker 2.0');
-- insert or replace into totemdb.locale values ('pt-br', '2611_URL', '/totem/images/products/2611.png');

insert or replace into totemdb.locale values ('pt-br', '2612', 'Mega Stacker 3.0');
insert or replace into totemdb.locale values ('pt-br', '2612_URL', '/totem/images/products/2612.png');
insert or replace into totemdb.locale values ('pt-br', '2613', 'Combo Mega Stacker 3.0');
-- insert or replace into totemdb.locale values ('pt-br', '2613_URL', '/totem/images/products/2613.png');

insert or replace into totemdb.locale values ('pt-br', '2614', 'Mega Stacker 4.0');
insert or replace into totemdb.locale values ('pt-br', '2614_URL', '/totem/images/products/2614.png');
insert or replace into totemdb.locale values ('pt-br', '2615', 'Combo Mega Stacker 4.0');
-- insert or replace into totemdb.locale values ('pt-br', '2615_URL', '/totem/images/products/2615.png');

insert or replace into totemdb.locale values ('pt-br', '1050', 'WHOPPER®');
insert or replace into totemdb.locale values ('pt-br', '1050_URL', '/totem/images/products/1050.png');
insert or replace into totemdb.locale values ('pt-br', '1051', 'Combo WHOPPER®');
insert or replace into totemdb.locale values ('pt-br', '1051_URL', '/totem/images/products/1051.png');

insert or replace into totemdb.locale values ('pt-br', '1052', 'WHOPPER® Duplo');
insert or replace into totemdb.locale values ('pt-br', '1052_URL', '/totem/images/products/1052.png');
insert or replace into totemdb.locale values ('pt-br', '1053', 'Combo WHOPPER® Duplo');
-- insert or replace into totemdb.locale values ('pt-br', '1053_URL', '/totem/images/products/1053.png');

insert or replace into totemdb.locale values ('pt-br', '1600', 'WHOPPER JR.®');
insert or replace into totemdb.locale values ('pt-br', '1600_URL', '/totem/images/products/1600.png');
insert or replace into totemdb.locale values ('pt-br', '1601', 'Combo WHOPPER JR.®');
-- insert or replace into totemdb.locale values ('pt-br', '1601_URL', '/totem/images/products/1601.png');

insert or replace into totemdb.locale values ('pt-br', '1700', 'WHOPPER® Furioso');
insert or replace into totemdb.locale values ('pt-br', '1700_URL', '/totem/images/products/1700.png');
insert or replace into totemdb.locale values ('pt-br', '1701', 'Combo WHOPPER® Furioso');
-- insert or replace into totemdb.locale values ('pt-br', '1701_URL', '/totem/images/products/1701.png');

insert or replace into totemdb.locale values ('pt-br', '2604', 'Stacker Triplo');
insert or replace into totemdb.locale values ('pt-br', '2604_URL', '/totem/images/products/2604.png');
insert or replace into totemdb.locale values ('pt-br', '2605', 'Combo Stacker Triplo');
-- insert or replace into totemdb.locale values ('pt-br', '2605_URL', '/totem/images/products/2605.png');

insert or replace into totemdb.locale values ('pt-br', '5000074', 'Picanha');
insert or replace into totemdb.locale values ('pt-br', '5000074_URL', '/totem/images/products/5000074.png');
insert or replace into totemdb.locale values ('pt-br', '5000075', 'Combo Picanha');
-- insert or replace into totemdb.locale values ('pt-br', '5000075_URL', '/totem/images/products/5000075.png');

insert or replace into totemdb.locale values ('pt-br', '5000413', 'Picanha Barbecue Bacon');
insert or replace into totemdb.locale values ('pt-br', '5000413_URL', '/totem/images/products/5000413.png');
insert or replace into totemdb.locale values ('pt-br', '7100001', 'Combo Picanha Barbecue Bacon');
-- insert or replace into totemdb.locale values ('pt-br', '7100001_URL', '/totem/images/products/7100001.png');

insert or replace into totemdb.locale values ('pt-br', '7100023', 'Big King™');
insert or replace into totemdb.locale values ('pt-br', '7100023_URL', '/totem/images/products/7100023.png');
insert or replace into totemdb.locale values ('pt-br', '7100018', 'Combo Big King™');
-- insert or replace into totemdb.locale values ('pt-br', '7100018_URL', '/totem/images/products/7100018.png');

insert or replace into totemdb.locale values ('pt-br', '1804', 'Cheddar Duplo');
insert or replace into totemdb.locale values ('pt-br', '1804_URL', '/totem/images/products/1804.png');
insert or replace into totemdb.locale values ('pt-br', '1805', 'Combo Cheddar Duplo');
-- insert or replace into totemdb.locale values ('pt-br', '1805_URL', '/totem/images/products/1805.png');

insert or replace into totemdb.locale values ('pt-br', '2106', 'Cheeseburger Duplo com Bacon');
insert or replace into totemdb.locale values ('pt-br', '2106_URL', '/totem/images/products/2106.png');
insert or replace into totemdb.locale values ('pt-br', '2107', 'Combo Cheeseburger Duplo com Bacon');
-- insert or replace into totemdb.locale values ('pt-br', '2107_URL', '/totem/images/products/2107.png');

insert or replace into totemdb.locale values ('pt-br', '7100021', 'Cheeseburger com Bacon');
insert or replace into totemdb.locale values ('pt-br', '7100021_URL', '/totem/images/products/7100021.png');
insert or replace into totemdb.locale values ('pt-br', '7100016', 'Cheeseburger com Bacon');
-- insert or replace into totemdb.locale values ('pt-br', '7100016_URL', '/totem/images/products/7100016.png');

insert or replace into totemdb.locale values ('pt-br', '2100', 'Cheeseburger');
insert or replace into totemdb.locale values ('pt-br', '2100_URL', '/totem/images/products/2100.png');
insert or replace into totemdb.locale values ('pt-br', '2101', 'Cheeseburger');
-- insert or replace into totemdb.locale values ('pt-br', '2101_URL', '/totem/images/products/2101.png');

insert or replace into totemdb.locale values ('pt-br', '2050', 'Hambúrguer');
insert or replace into totemdb.locale values ('pt-br', '2050_URL', '/totem/images/products/2050.png');



-- hot dogs
insert or replace into totemdb.locale values ('pt-br', '7100048', 'Grill Dog Clássico');
insert or replace into totemdb.locale values ('pt-br', '7100048_URL', '/totem/images/products/7100048.png');
insert or replace into totemdb.locale values ('pt-br', '7000016', 'Combo Grill Dog Clássico');
-- insert or replace into totemdb.locale values ('pt-br', '7000016_URL', '/totem/images/products/7000016.png');

insert or replace into totemdb.locale values ('pt-br', '7100049', 'Grill Dog Cheddar e Bacon');
insert or replace into totemdb.locale values ('pt-br', '7100049_URL', '/totem/images/products/7100049.png');
insert or replace into totemdb.locale values ('pt-br', '7000022', 'Combo Grill Dog Cheddar e Bacon');
-- insert or replace into totemdb.locale values ('pt-br', '7000022_URL', '/totem/images/products/7000022.png');


-- hamburgueres de frango
insert or replace into totemdb.locale values ('pt-br', '3100', 'Chicken Crisp');
insert or replace into totemdb.locale values ('pt-br', '3100_URL', '/totem/images/products/3100.png');
insert or replace into totemdb.locale values ('pt-br', '3101', 'Combo Chicken Crisp');
-- insert or replace into totemdb.locale values ('pt-br', '3101_URL', '/totem/images/products/3101.png');

insert or replace into totemdb.locale values ('pt-br', '2700', 'Chicken Sandwich');
insert or replace into totemdb.locale values ('pt-br', '2700_URL', '/totem/images/products/2700.png');
insert or replace into totemdb.locale values ('pt-br', '2701', 'Combo Chicken Sandwich');
-- insert or replace into totemdb.locale values ('pt-br', '2701_URL', '/totem/images/products/2701.png');

insert or replace into totemdb.locale values ('pt-br', '2064', 'Chicken Junior');
insert or replace into totemdb.locale values ('pt-br', '2064_URL', '/totem/images/products/2064.png');
insert or replace into totemdb.locale values ('pt-br', '2065', 'Combo Chicken Junior');
-- insert or replace into totemdb.locale values ('pt-br', '2065_URL', '/totem/images/products/2605.png');

-- Saladas
insert or replace into totemdb.locale values ('pt-br', '7100033', 'Veggie Burger');
insert or replace into totemdb.locale values ('pt-br', '7100033_URL', '/totem/images/products/7100033.png');
insert or replace into totemdb.locale values ('pt-br', '7000005', 'Combo Veggie Burger');
-- insert or replace into totemdb.locale values ('pt-br', '7000005_URL', '/totem/images/products/7000005.png');

insert or replace into totemdb.locale values ('pt-br', '7800001', 'BK Levíssima');
insert or replace into totemdb.locale values ('pt-br', '7800001_URL', '/totem/images/products/7800001.png');


-- Bebidas
insert or replace into totemdb.locale values ('pt-br', '9008', 'Free Refil de Refrigerante');
insert or replace into totemdb.locale values ('pt-br', '9008_URL', '/totem/images/products/9008.png');
insert or replace into totemdb.locale values ('pt-br', '7500003', 'Free Refil de Chá');
insert or replace into totemdb.locale values ('pt-br', '7500003_URL', '/totem/images/products/7500003.png');

insert or replace into totemdb.locale values ('pt-br', '9052', 'H2OH!® Limão');
insert or replace into totemdb.locale values ('pt-br', '9052_URL', '/totem/images/products/9052.png');
insert or replace into totemdb.locale values ('pt-br', '9053', 'H2OH!® Citrus');
insert or replace into totemdb.locale values ('pt-br', '9053_URL', '/totem/images/products/9053.png');
insert or replace into totemdb.locale values ('pt-br', '9054', 'H2OH!® Laranja');
insert or replace into totemdb.locale values ('pt-br', '9054_URL', '/totem/images/products/9054.png');

insert or replace into totemdb.locale values ('pt-br', '9103', 'SuFresh® de Uva');
-- insert or replace into totemdb.locale values ('pt-br', '9103_URL', '/totem/images/products/9103.png');
insert or replace into totemdb.locale values ('pt-br', '9104', 'SuFresh® de Uva Light');
-- insert or replace into totemdb.locale values ('pt-br', '9104_URL', '/totem/images/products/9104.png');
insert or replace into totemdb.locale values ('pt-br', '9101', 'SuFresh® de Pêssego');
-- insert or replace into totemdb.locale values ('pt-br', '9101_URL', '/totem/images/products/9101.png');
insert or replace into totemdb.locale values ('pt-br', '9102', 'SuFresh® de Pêssego Light');
-- insert or replace into totemdb.locale values ('pt-br', '9102_URL', '/totem/images/products/9102.png');
insert or replace into totemdb.locale values ('pt-br', '9105', 'SuFresh® de Maracujá');
-- insert or replace into totemdb.locale values ('pt-br', '9105_URL', '/totem/images/products/9105.png');
insert or replace into totemdb.locale values ('pt-br', '9106', 'SuFresh® de Laranja');
-- insert or replace into totemdb.locale values ('pt-br', '9106_URL', '/totem/images/products/9106.png');
insert or replace into totemdb.locale values ('pt-br', '9107', 'SuFresh® de Maçã');
-- insert or replace into totemdb.locale values ('pt-br', '9107_URL', '/totem/images/products/9107.png');

/*insert or replace into totemdb.locale values ('pt-br', '9055', 'Lipton® Iced Tea Limão');
insert or replace into totemdb.locale values ('pt-br', '9055_URL', '/totem/images/products/9055.png');
insert or replace into totemdb.locale values ('pt-br', '9055', 'Lipton® Iced Tea Pêssego');
insert or replace into totemdb.locale values ('pt-br', '9055_URL', '/totem/images/products/9055.png');
*/
/*insert or replace into totemdb.locale values ('pt-br', '9049', 'Copo de Água');
insert or replace into totemdb.locale values ('pt-br', '9049_URL', '/totem/images/products/9049.png');
*/

-- acompanhamentos
insert or replace into totemdb.locale values ('pt-br', '6011', 'Batata Pequena');
-- insert or replace into totemdb.locale values ('pt-br', '6011_URL', '/totem/images/products/6011.png');
insert or replace into totemdb.locale values ('pt-br', '6012', 'Batata Média');
insert or replace into totemdb.locale values ('pt-br', '6012_URL', '/totem/images/products/6012.png');
insert or replace into totemdb.locale values ('pt-br', '6013', 'Batata Grande');
-- insert or replace into totemdb.locale values ('pt-br', '6013_URL', '/totem/images/products/6013.png');
insert or replace into totemdb.locale values ('pt-br', '6020', 'Batata Suprema Individual');
-- insert or replace into totemdb.locale values ('pt-br', '6020_URL', '/totem/images/products/6020.png');
insert or replace into totemdb.locale values ('pt-br', '6019', 'Batata Suprema');
insert or replace into totemdb.locale values ('pt-br', '6019_URL', '/totem/images/products/6019.png');
insert or replace into totemdb.locale values ('pt-br', '6025', 'Batata Furiosa Individual');
-- insert or replace into totemdb.locale values ('pt-br', '6025_URL', '/totem/images/products/6025.png');
insert or replace into totemdb.locale values ('pt-br', '6027', 'Batata Furiosa Grande');
-- insert or replace into totemdb.locale values ('pt-br', '6027_URL', '/totem/images/products/6027.png');

insert or replace into totemdb.locale values ('pt-br', '6021', 'Trio Supremo');
insert or replace into totemdb.locale values ('pt-br', '6021_URL', '/totem/images/products/6021.png');

insert or replace into totemdb.locale values ('pt-br', '6028', 'Trio Furioso');
-- insert or replace into totemdb.locale values ('pt-br', '6028_URL', '/totem/images/products/6028.png');

insert or replace into totemdb.locale values ('pt-br', '7300002', 'Chicken Fries');
insert or replace into totemdb.locale values ('pt-br', '7300002_URL', '/totem/images/products/7300002.png');

insert or replace into totemdb.locale values ('pt-br', '7300005', 'Onion Rings Pequeno');
-- insert or replace into totemdb.locale values ('pt-br', '7300005_URL', '/totem/images/products/7300005.png');
insert or replace into totemdb.locale values ('pt-br', '6017', 'Onion Rings Médio');
insert or replace into totemdb.locale values ('pt-br', '6017_URL', '/totem/images/products/6017.png');
insert or replace into totemdb.locale values ('pt-br', '6018', 'Onion Rings Grande');
-- insert or replace into totemdb.locale values ('pt-br', '6018_URL', '/totem/images/products/6018.png');

insert or replace into totemdb.locale values ('pt-br', '6508', 'BK Chicken 4 unidades');
-- insert or replace into totemdb.locale values ('pt-br', '6508_URL', '/totem/images/products/6508.png');

insert or replace into totemdb.locale values ('pt-br', '6522', 'BK Chicken 6 unidades');
insert or replace into totemdb.locale values ('pt-br', '6522_URL', '/totem/images/products/6522.png');

insert or replace into totemdb.locale values ('pt-br', '7300001', 'BK Chicken 10 unidades');
-- insert or replace into totemdb.locale values ('pt-br', '7300001_URL', '/totem/images/products/7300001.png');

insert or replace into totemdb.locale values ('pt-br', '7300014', 'Balde de Batata');
insert or replace into totemdb.locale values ('pt-br', '7300014_URL', '/totem/images/products/7300014.png');


-- Sobremesas
insert or replace into totemdb.locale values ('pt-br', '20000', 'Casquinha de Baunilha');
-- insert or replace into totemdb.locale values ('pt-br', '20000_URL', '/totem/images/products/20000.png');
insert or replace into totemdb.locale values ('pt-br', '20001', 'Casquinha de Chocolate');
-- insert or replace into totemdb.locale values ('pt-br', '20001_URL', '/totem/images/products/20001.png');
insert or replace into totemdb.locale values ('pt-br', '20002', 'Casquinha Mista');
-- insert or replace into totemdb.locale values ('pt-br', '20002_URL', '/totem/images/products/20002.png');

insert or replace into totemdb.locale values ('pt-br', '8000001', 'Casquinha Recheada de Chocolate');
-- insert or replace into totemdb.locale values ('pt-br', '8000001_URL', '/totem/images/products/8000001.png');
insert or replace into totemdb.locale values ('pt-br', '8000006', 'Casquinha Recheada de Sensação');
-- insert or replace into totemdb.locale values ('pt-br', '8000006_URL', '/totem/images/products/8000006.png');
insert or replace into totemdb.locale values ('pt-br', '8000007', 'Casquinha Recheada de Doce de Leite');
-- insert or replace into totemdb.locale values ('pt-br', '8000007_URL', '/totem/images/products/8000007.png');
insert or replace into totemdb.locale values ('pt-br', '8000008', 'Casquinha Recheada de Negresco');
-- insert or replace into totemdb.locale values ('pt-br', '8000008_URL', '/totem/images/products/8000008.png');
insert or replace into totemdb.locale values ('pt-br', '8000012', 'Casquinha Recheada de Ovomaltine');
-- insert or replace into totemdb.locale values ('pt-br', '8000012_URL', '/totem/images/products/8000012.png');

insert or replace into totemdb.locale values ('pt-br', '5000278', 'BK Mix Sensação');
-- insert or replace into totemdb.locale values ('pt-br', '5000278_URL', '/totem/images/products/5000278.png');
insert or replace into totemdb.locale values ('pt-br', '5000420', 'BK Mix Negresco');
-- insert or replace into totemdb.locale values ('pt-br', '5000420_URL', '/totem/images/products/5000420.png');
insert or replace into totemdb.locale values ('pt-br', '6000072', 'BK Mix Ovomaltine');
-- insert or replace into totemdb.locale values ('pt-br', '6000072_URL', '/totem/images/products/6000072.png');

insert or replace into totemdb.locale values ('pt-br', '20006', 'Sundae de Baunilha');
insert or replace into totemdb.locale values ('pt-br', '20006_URL', '/totem/images/products/20006.png');
insert or replace into totemdb.locale values ('pt-br', '20007', 'Sundae de Chocolate');
-- insert or replace into totemdb.locale values ('pt-br', '20007_URL', '/totem/images/products/20007.png');
insert or replace into totemdb.locale values ('pt-br', '20008', 'Sundae Mista');
-- insert or replace into totemdb.locale values ('pt-br', '20008_URL', '/totem/images/products/20008.png');
insert or replace into totemdb.locale values ('pt-br', '8000013', 'Sundae Ovomaltine');
-- insert or replace into totemdb.locale values ('pt-br', '8000013_URL', '/totem/images/products/8000013.png');
insert or replace into totemdb.locale values ('pt-br', '8000025', 'Sundae Romeu e Julieta');
-- insert or replace into totemdb.locale values ('pt-br', '8000025_URL', '/totem/images/products/8000025.png');

insert or replace into totemdb.locale values ('pt-br', '20009', 'Mega Sundae Baunilha');
-- insert or replace into totemdb.locale values ('pt-br', '20009_URL', '/totem/images/products/20009.png');
insert or replace into totemdb.locale values ('pt-br', '20010', 'Mega Sundae Chocolate');
-- insert or replace into totemdb.locale values ('pt-br', '20010_URL', '/totem/images/products/20010.png');
insert or replace into totemdb.locale values ('pt-br', '20011', 'Mega Sundae Mista');
-- insert or replace into totemdb.locale values ('pt-br', '20011_URL', '/totem/images/products/20011.png');

insert or replace into totemdb.locale values ('pt-br', '20026', 'BK Shake Chocolate');
-- insert or replace into totemdb.locale values ('pt-br', '20011_URL', '/totem/images/products/20011.png');
insert or replace into totemdb.locale values ('pt-br', '20029', 'BK Shake Morango');
-- insert or replace into totemdb.locale values ('pt-br', '20011_URL', '/totem/images/products/20011.png');
insert or replace into totemdb.locale values ('pt-br', '20027', 'BK Shake Baunilha');
-- insert or replace into totemdb.locale values ('pt-br', '20011_URL', '/totem/images/products/20011.png');



-- Combo Kids
insert or replace into totemdb.locale values ('pt-br', '7100012', 'Combo Kids');
insert or replace into totemdb.locale values ('pt-br', '7100012_URL', '/totem/images/products/7100012.png');

insert or replace into totemdb.locale values ('pt-br', '6501', 'KM Hamburguer');
-- insert or replace into totemdb.locale values ('pt-br', '6501_URL', '/totem/images/products/6501.png');

insert or replace into totemdb.locale values ('pt-br', '6503', 'KM Cheeseburger');
-- insert or replace into totemdb.locale values ('pt-br', '6503_URL', '/totem/images/products/6503.png');

insert or replace into totemdb.locale values ('pt-br', '6509', 'KM BK Chicken 4 unidades');
-- insert or replace into totemdb.locale values ('pt-br', '6509_URL', '/totem/images/products/6509.png');

insert or replace into totemdb.locale values ('pt-br', '7900001', 'KM BK Chicken 10 unidades');
-- insert or replace into totemdb.locale values ('pt-br', '7900001_URL', '/totem/images/products/7900001.png');

-- init products info

-- hamburgueres de carne
insert or replace into totemdb.productinfo values(7100054, '7100054', '7100054_URL');
insert or replace into totemdb.productinfo values(6000605, '6000605', '6000605_URL');

insert or replace into totemdb.productinfo values(7100053, '7100053', '7100053_URL');
insert or replace into totemdb.productinfo values(6000604, '6000604', '6000604_URL');

insert or replace into totemdb.productinfo values(7100003, '7100003', '7100003_URL');
insert or replace into totemdb.productinfo values(7100002, '7100002', '7100002_URL');

insert or replace into totemdb.productinfo values(7100051, '7100051', '7100051_URL');
insert or replace into totemdb.productinfo values(7000019, '7000019', '7000019_URL');

insert or replace into totemdb.productinfo values(7100036, '7100036', '7100036_URL');
insert or replace into totemdb.productinfo values(7000007, '7000007', '7000007_URL');

insert or replace into totemdb.productinfo values(2610, '2610', '2610_URL');
insert or replace into totemdb.productinfo values(2611, '2611', '2611_URL');

insert or replace into totemdb.productinfo values(2612, '2612', '2612_URL');
insert or replace into totemdb.productinfo values(2613, '2613', '2613_URL');

insert or replace into totemdb.productinfo values(2614, '2614', '2614_URL');
insert or replace into totemdb.productinfo values(2615, '2615', '2615_URL');

insert or replace into totemdb.productinfo values(1050, '1050', '1050_URL');
insert or replace into totemdb.productinfo values(1051, '1051', '1051_URL');

insert or replace into totemdb.productinfo values(1052, '1052', '1052_URL');
insert or replace into totemdb.productinfo values(1053, '1053', '1053_URL');

insert or replace into totemdb.productinfo values(1600, '1600', '1600_URL');
insert or replace into totemdb.productinfo values(1601, '1601', '1601_URL');

insert or replace into totemdb.productinfo values(1700, '1700', '1700_URL');
insert or replace into totemdb.productinfo values(1701, '1701', '1701_URL');

insert or replace into totemdb.productinfo values(2604, '2604', '2604_URL');
insert or replace into totemdb.productinfo values(2605, '2605', '2605_URL');

insert or replace into totemdb.productinfo values(5000074, '5000074', '5000074_URL');
insert or replace into totemdb.productinfo values(5000075, '5000075', '5000075_URL');

insert or replace into totemdb.productinfo values(5000413, '5000413', '5000413_URL');
insert or replace into totemdb.productinfo values(7100001, '7100001', '7100001_URL');

insert or replace into totemdb.productinfo values(7100023, '7100023', '7100023_URL');
insert or replace into totemdb.productinfo values(7100018, '7100018', '7100018_URL');

insert or replace into totemdb.productinfo values(1804, '1804', '1804_URL');
insert or replace into totemdb.productinfo values(1805, '1805', '1805_URL');

insert or replace into totemdb.productinfo values(2106, '2106', '2106_URL');
insert or replace into totemdb.productinfo values(2107, '2107', '2107_URL');

insert or replace into totemdb.productinfo values(7100021, '7100021', '7100021_URL');
insert or replace into totemdb.productinfo values(7100016, '7100016', '7100016_URL');

insert or replace into totemdb.productinfo values(2100, '2100', '2100_URL');
insert or replace into totemdb.productinfo values(2101, '2101', '2101_URL');

insert or replace into totemdb.productinfo values(2050, '2050', '2050_URL');


-- hot dog
insert or replace into totemdb.productinfo values (7100048, '7100048', '7100048_URL');
insert or replace into totemdb.productinfo values (7000016, '7000016', '7000016_URL');

insert or replace into totemdb.productinfo values (7100049, '7100049', '7100049_URL');
insert or replace into totemdb.productinfo values (7000022, '7000022', '7000022_URL');

-- hamburgueres de frango
insert or replace into totemdb.productinfo values (3100, '3100', '3100_URL');
insert or replace into totemdb.productinfo values (3101, '3101', '3101_URL');

insert or replace into totemdb.productinfo values (2700, '2700', '2700_URL');
insert or replace into totemdb.productinfo values (2701, '2701', '2701_URL');

insert or replace into totemdb.productinfo values (2064, '2064', '2064_URL');
insert or replace into totemdb.productinfo values (2065, '2065', '2065_URL');

-- saladas
insert or replace into totemdb.productinfo values (7100033, '7100033', '7100033_URL');
insert or replace into totemdb.productinfo values (7000005, '7000005', '7000005_URL');

insert or replace into totemdb.productinfo values (7800001, '7800001', '7800001_URL');

-- bebidas
insert or replace into totemdb.productinfo values (9008, '9008', '9008_URL');
insert or replace into totemdb.productinfo values (7500003, '7500003', '7500003_URL');
insert or replace into totemdb.productinfo values (9052, '9052', '9052_URL');
insert or replace into totemdb.productinfo values (9053, '9053', '9053_URL');
insert or replace into totemdb.productinfo values (9054, '9054', '9054_URL');

insert or replace into totemdb.productinfo values (9103, '9103', '9103_URL');
insert or replace into totemdb.productinfo values (9104, '9104', '9104_URL');
insert or replace into totemdb.productinfo values (9101, '9101', '9101_URL');
insert or replace into totemdb.productinfo values (9102, '9102', '9102_URL');
insert or replace into totemdb.productinfo values (9105, '9105', '9105_URL');
insert or replace into totemdb.productinfo values (9106, '9106', '9106_URL');
insert or replace into totemdb.productinfo values (9107, '9107', '9107_URL');

-- Acompanhamentos
insert or replace into totemdb.productinfo values (6011, '6011', '6011_URL');
insert or replace into totemdb.productinfo values (6012, '6012', '6012_URL');
insert or replace into totemdb.productinfo values (6013, '6013', '6013_URL');
insert or replace into totemdb.productinfo values (6020, '6020', '6020_URL');
insert or replace into totemdb.productinfo values (6019, '6019', '6019_URL');
insert or replace into totemdb.productinfo values (6025, '6025', '6025_URL');
insert or replace into totemdb.productinfo values (6027, '6027', '6027_URL');
insert or replace into totemdb.productinfo values (6021, '6021', '6021_URL');
insert or replace into totemdb.productinfo values (6028, '6028', '6028_URL');
insert or replace into totemdb.productinfo values (7300002, '7300002', '7300002_URL');
insert or replace into totemdb.productinfo values (7300005, '7300005', '7300005_URL');
insert or replace into totemdb.productinfo values (6017, '6017', '6017_URL');
insert or replace into totemdb.productinfo values (6018, '6018', '6018_URL');
insert or replace into totemdb.productinfo values (6508, '6508', '6508_URL');
insert or replace into totemdb.productinfo values (6522, '6522', '6522_URL');
insert or replace into totemdb.productinfo values (7300001, '7300001', '7300001_URL');
insert or replace into totemdb.productinfo values (7300014, '7300014', '7300014_URL');

-- Sobremesas
insert or replace into totemdb.productinfo values (7300014, '7300014', '7300014_URL');
insert or replace into totemdb.productinfo values (20000, '20000', '20000_URL');
insert or replace into totemdb.productinfo values (20001, '20001', '20001_URL');
insert or replace into totemdb.productinfo values (20002, '20002', '20002_URL');
insert or replace into totemdb.productinfo values (8000001, '8000001', '8000001_URL');
insert or replace into totemdb.productinfo values (8000006, '8000006', '8000006_URL');
insert or replace into totemdb.productinfo values (8000007, '8000007', '8000007_URL');
insert or replace into totemdb.productinfo values (8000008, '8000008', '8000008_URL');
insert or replace into totemdb.productinfo values (8000012, '8000012', '8000012_URL');
insert or replace into totemdb.productinfo values (5000278, '5000278', '5000278_URL');
insert or replace into totemdb.productinfo values (5000420, '5000420', '5000420_URL');
insert or replace into totemdb.productinfo values (6000072, '6000072', '6000072_URL');
insert or replace into totemdb.productinfo values (20006, '20006', '20006_URL');
insert or replace into totemdb.productinfo values (20007, '20007', '20007_URL');
insert or replace into totemdb.productinfo values (20008, '20008', '20008_URL');
insert or replace into totemdb.productinfo values (8000013, '8000013', '8000013_URL');
insert or replace into totemdb.productinfo values (8000025, '8000025', '8000025_URL');
insert or replace into totemdb.productinfo values (20009, '20009', '20009_URL');
insert or replace into totemdb.productinfo values (20010, '20010', '20010_URL');
insert or replace into totemdb.productinfo values (20011, '20011', '20011_URL');


-- Combo Kids
insert or replace into totemdb.productinfo values (7100012, '7100012', '7100012_URL');
insert or replace into totemdb.productinfo values (6501, '6501', '6501_URL');
insert or replace into totemdb.productinfo values (6503, '6503', '6503_URL');
insert or replace into totemdb.productinfo values (6509, '6509', '6509_URL');
insert or replace into totemdb.productinfo values (7900001, '7900001', '7900001_URL');

-- init coupons
insert or replace into totemdb.locale values ('pt-br', 'COUPON_1', 'Cupom Promocional 1');
insert or replace into totemdb.locale values ('pt-br', 'COUPON_2', 'Cupom Promocional 2');
insert or replace into totemdb.locale values ('pt-br', 'COUPON_3', 'Cupom Promocional 3');

insert or replace into totemdb.coupon values ('AAAA', 'white', 'cupom 1', 1, 10.00, 'COUPON_1', 'COUPON_1_URL');
insert or replace into totemdb.coupon values ('AAAB', 'yellow', 'cupom 2', 1, 10.00, 'COUPON_2', 'COUPON_2_URL');
insert or replace into totemdb.coupon values ('AAAC', 'red', 'cupom 3', 1, 10.00, 'COUPON_3', 'COUPON_3_URL');

-- init couponProducts
insert or replace into totemdb.couponproduct values ('AAAA', 1051);
insert or replace into totemdb.couponproduct values ('AAAA', 1053);

insert or replace into totemdb.couponproduct values ('AAAB', 1053);
insert or replace into totemdb.couponproduct values ('AAAC', 6000266);

-- init sale options
-- hamburgueres de carne
insert or replace into totemdb.productSaleOptions values (7100054, 6000605);
insert or replace into totemdb.productSaleOptions values (7100053, 6000604);
insert or replace into totemdb.productSaleOptions values (7100003, 7100002);
insert or replace into totemdb.productSaleOptions values (7100051, 7000019);
insert or replace into totemdb.productSaleOptions values (7100036, 7000007);
insert or replace into totemdb.productSaleOptions values (2610, 2611);
insert or replace into totemdb.productSaleOptions values (2612, 2613);
insert or replace into totemdb.productSaleOptions values (2614, 2615);
insert or replace into totemdb.productSaleOptions values (1050, 1051);
insert or replace into totemdb.productSaleOptions values (1052, 1053);
insert or replace into totemdb.productSaleOptions values (1600, 1601);
insert or replace into totemdb.productSaleOptions values (1700, 1701);
insert or replace into totemdb.productSaleOptions values (2604, 2605);
insert or replace into totemdb.productSaleOptions values (5000074, 5000075);
insert or replace into totemdb.productSaleOptions values (5000413, 7100001);
insert or replace into totemdb.productSaleOptions values (7100023, 7100018);
insert or replace into totemdb.productSaleOptions values (1804, 1805);
insert or replace into totemdb.productSaleOptions values (2106, 2107);
insert or replace into totemdb.productSaleOptions values (7100021, 7100016);
insert or replace into totemdb.productSaleOptions values (2100, 2101);

-- hot dogs
insert or replace into totemdb.productSaleOptions values (7100048, 7000016);
insert or replace into totemdb.productSaleOptions values (7100049, 7000022);

-- hamburgueres de frango
insert or replace into totemdb.productSaleOptions values (3100, 3101);
insert or replace into totemdb.productSaleOptions values (2700, 2701);
insert or replace into totemdb.productSaleOptions values (2064, 2065);

-- saladas
insert or replace into totemdb.productSaleOptions values (7100033, 7000005);


-- init banners data
insert or replace into totemdb.locale values ('pt-br', 'BANNER_1_URL', '/totem/images/banners/2por15.png');
insert or replace into totemdb.Banner values ('BANNER_1_URL');

-- init suggestions
insert or replace into totemdb.suggestion values (730003);
insert or replace into totemdb.suggestion values (4000);
insert or replace into totemdb.suggestion values (8200019);
insert or replace into totemdb.suggestion values (20006);
insert or replace into totemdb.suggestion values (20027);
insert or replace into totemdb.suggestion values (20031);


-- init option label l10n
insert or replace into totemdb.locale values ('pt-br', '1050_8200000', 'Deseja personalizar seu Whooper?');
insert or replace into totemdb.locale values ('pt-br', '1051_7300000', 'Escolha o Acompanhamento');
insert or replace into totemdb.locale values ('pt-br', 'SIDE_CHOOSE', 'Escolha o Acompanhamento');
insert or replace into totemdb.locale values ('pt-br', '1051_7500000', 'Escolha a Bebida');
insert or replace into totemdb.locale values ('pt-br', '1051_9900000', 'Deseja incluir Chicken Fries?');
insert or replace into totemdb.locale values ('pt-br', '7300002_8800000', 'Escolha o Molho Chicken Fries');
insert or replace into totemdb.locale values ('pt-br', '1051_10025000', 'Deseja incluir BK Mix?');
insert or replace into totemdb.locale values ('pt-br', 'EXTRA_BKMIX', 'Deseja incluir BK Mix?');
insert or replace into totemdb.locale values ('pt-br', 'INCLUDE_EXTRAS', 'Deseja adicionar extras?');
insert or replace into totemdb.locale values ('pt-br', 'INCLUDE_FLAVOR', 'Escolha a massa');
insert or replace into totemdb.locale values ('pt-br', 'COUPON_COLOR', 'Escolha a cor do cupom');

-- init option labels
insert or replace into totemdb.optionlabel values (8200000, '1050', '1050_8200000', '#000000');
insert or replace into totemdb.optionlabel values (7300000, '1051', '1051_7300000', '#eeaa03');
insert or replace into totemdb.optionlabel values (7500000, '1051', '1051_7500000', '#A2007D');
insert or replace into totemdb.optionlabel values (9900000, '1051', '1051_9900000', '#000000');
insert or replace into totemdb.optionlabel values (8800000, '7300002', '7300002_8800000', '#eeaa03');
insert or replace into totemdb.optionlabel values (10025000, '1051', '1051_10025000', '#eeaa03');
insert or replace into totemdb.optionlabel values (10027000, '8000028', 'INCLUDE_EXTRAS', '#eeaa03');
insert or replace into totemdb.optionlabel values (10026000, '8000028', 'INCLUDE_FLAVOR', '#eeaa03');
insert or replace into totemdb.optionlabel values (10027000, '8000029', 'INCLUDE_EXTRAS', '#eeaa03');
insert or replace into totemdb.optionlabel values (10026000, '8000029', 'INCLUDE_FLAVOR', '#eeaa03');

insert or replace into totemdb.optionlabel values (6000000, '6000266', 'COUPON_COLOR', '#000000');
insert or replace into totemdb.optionlabel values (10025000, '6000266', 'EXTRA_BKMIX', '#000000');
insert or replace into totemdb.optionlabel values (10025000, '6000266', 'EXTRA_BKMIX', '#000000');
insert or replace into totemdb.optionlabel values (8200000, '7100023', 'INCLUDE_EXTRAS', '#000000');
insert or replace into totemdb.optionlabel values (10004000, '90001011', 'SIDE_CHOOSE', '#000000');

insert or replace into totemdb.Configuration values ('time', '60');

COMMIT TRANSACTION;