-- MySQL dump 10.13  Distrib 5.7.33, for Win64 (x86_64)
--
-- Host: localhost    Database: smartMiniFridge
-- ------------------------------------------------------
-- Server version	5.5.5-10.3.27-MariaDB-0+deb10u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `acties`
--

DROP TABLE IF EXISTS `acties`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `acties` (
  `actieId` int(11) NOT NULL AUTO_INCREMENT,
  `beschrijving` varchar(45) NOT NULL,
  PRIMARY KEY (`actieId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `acties`
--

LOCK TABLES `acties` WRITE;
/*!40000 ALTER TABLE `acties` DISABLE KEYS */;
/*!40000 ALTER TABLE `acties` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device`
--

DROP TABLE IF EXISTS `device`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device` (
  `deviceId` int(11) NOT NULL AUTO_INCREMENT,
  `naam` varchar(45) NOT NULL,
  `eenheid` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`deviceId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device`
--

LOCK TABLES `device` WRITE;
/*!40000 ALTER TABLE `device` DISABLE KEYS */;
/*!40000 ALTER TABLE `device` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historiek`
--

DROP TABLE IF EXISTS `historiek`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `historiek` (
  `historiekId` int(11) NOT NULL AUTO_INCREMENT,
  `datum` datetime NOT NULL,
  `waarde` varchar(45) DEFAULT NULL,
  `commentaar` varchar(45) NOT NULL,
  `deviceId` int(11) DEFAULT NULL,
  `actieId` int(11) DEFAULT NULL,
  `productId` int(11) DEFAULT NULL,
  PRIMARY KEY (`historiekId`),
  KEY `productId_idx` (`productId`),
  CONSTRAINT `productId` FOREIGN KEY (`productId`) REFERENCES `producten` (`productId`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=334 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historiek`
--

LOCK TABLES `historiek` WRITE;
/*!40000 ALTER TABLE `historiek` DISABLE KEYS */;
INSERT INTO `historiek` VALUES (21,'2021-06-11 15:04:09','Fruitsap','ingescand',NULL,1,5),(23,'2021-06-11 15:04:13','Fruitsap','uitgescand',NULL,2,5),(41,'2021-06-11 15:23:38','Nalu','ingescand',NULL,1,7),(43,'2021-06-11 15:23:43','Nalu','uitgescand',NULL,2,7),(44,'2021-06-11 15:23:46','0','slot uit',4,7,NULL),(46,'2021-06-11 15:23:51','1','slot aan',4,6,NULL),(56,'2021-06-11 15:27:05','Primus','ingescand',NULL,1,15),(59,'2021-06-11 15:27:17','Primus','uitgescand',NULL,2,15),(76,'2021-06-11 15:34:39','0','slot uit',4,7,NULL),(78,'2021-06-11 15:34:44','1','slot aan',4,6,NULL),(81,'2021-06-11 15:34:55','Primus','ingescand',NULL,1,15),(83,'2021-06-11 15:35:02','Primus','ingescand',NULL,1,15),(85,'2021-06-11 15:35:12','Primus','uitgescand',NULL,2,15),(102,'2021-06-11 15:36:48','0','slot uit',4,7,NULL),(103,'2021-06-11 15:36:53','1','slot aan',4,6,NULL),(107,'2021-06-11 15:37:07','Primus','uitgescand',NULL,2,15),(325,'2021-06-11 16:00:47','26.2','temp-meting',1,3,NULL);
/*!40000 ALTER TABLE `historiek` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `producten`
--

DROP TABLE IF EXISTS `producten`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `producten` (
  `productId` int(11) NOT NULL AUTO_INCREMENT,
  `naam` varchar(45) DEFAULT NULL,
  `barcode` varchar(45) DEFAULT NULL,
  `categorie` varchar(45) DEFAULT NULL,
  `aantal` int(11) DEFAULT NULL,
  `hoeveelheid` int(11) DEFAULT NULL,
  PRIMARY KEY (`productId`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producten`
--

LOCK TABLES `producten` WRITE;
/*!40000 ALTER TABLE `producten` DISABLE KEYS */;
INSERT INTO `producten` VALUES (1,'Stella Artois','786150000014','alcohol',0,330),(2,'Jupiler','5410228257479','alcohol',0,250),(3,'Spa Reine','5410013101703','water',0,1000),(4,'Chaudfontaine','5449000111654','water',0,1500),(5,'Fruitsap','5400141304305','fruitsap',0,1500),(6,'Chocomelk','5400141105001','melk',0,1000),(7,'Nalu','5060466511880','frisdrank',0,250),(8,'Ice Tea','8717163936795','frisdrank',0,330),(9,'Straffe hendrik 11°','5425017240648','alcohol',0,330),(10,'Bru','5410013305002','water',0,1250),(11,'Duvel Tripel hop citra','5411681401164','alcohol',0,330),(12,'Melk','5400141433586','melk',0,1000),(13,'Coca Cola','54491472','frisdrank',0,500),(14,'Vlaamse leeuw','5411663007513','alcohol',0,330),(15,'Primus','54085107','alcohol',0,330),(16,'7up lemon','5410188035209','frisdrank',0,330);
/*!40000 ALTER TABLE `producten` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-06-11 16:16:46
