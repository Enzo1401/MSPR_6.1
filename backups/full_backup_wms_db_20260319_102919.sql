-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 10.60.185.160    Database: wms_db
-- ------------------------------------------------------
-- Server version	5.5.5-10.11.14-MariaDB-0+deb12u2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `expeditions`
--

DROP TABLE IF EXISTS `expeditions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `expeditions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date_creation` datetime DEFAULT current_timestamp(),
  `id_site_depart` int(11) DEFAULT NULL,
  `id_transporteur` int(11) DEFAULT NULL,
  `statut` enum('Préparation','Quai','Expédié','Livré') DEFAULT 'Préparation',
  PRIMARY KEY (`id`),
  KEY `id_site_depart` (`id_site_depart`),
  KEY `id_transporteur` (`id_transporteur`),
  CONSTRAINT `expeditions_ibfk_1` FOREIGN KEY (`id_site_depart`) REFERENCES `sites` (`id`),
  CONSTRAINT `expeditions_ibfk_2` FOREIGN KEY (`id_transporteur`) REFERENCES `transporteurs` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `expeditions`
--

LOCK TABLES `expeditions` WRITE;
/*!40000 ALTER TABLE `expeditions` DISABLE KEYS */;
INSERT INTO `expeditions` VALUES (1,'2026-03-17 09:45:08',2,1,'Expédié'),(2,'2026-03-17 09:45:08',3,2,'Préparation'),(3,'2026-03-17 09:45:08',4,3,'Quai');
/*!40000 ALTER TABLE `expeditions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventaire`
--

DROP TABLE IF EXISTS `inventaire`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventaire` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `reference_sku` varchar(50) NOT NULL,
  `description` text DEFAULT NULL,
  `quantite_stock` int(11) DEFAULT 0,
  `seuil_alerte` int(11) DEFAULT 10,
  `id_site` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `reference_sku` (`reference_sku`),
  KEY `id_site` (`id_site`),
  CONSTRAINT `inventaire_ibfk_1` FOREIGN KEY (`id_site`) REFERENCES `sites` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventaire`
--

LOCK TABLES `inventaire` WRITE;
/*!40000 ALTER TABLE `inventaire` DISABLE KEYS */;
INSERT INTO `inventaire` VALUES (1,'PAL-EURO-01','Palettes Europe Standard',1200,10,2),(2,'SCAN-WIFI-Z','Lecteurs Radiofréquence Zebra',45,10,1),(3,'CART-LOG-M','Cartons de colisage taille M',5000,10,3),(4,'ETIQ-THERM','Rouleaux étiquettes thermiques',150,10,4);
/*!40000 ALTER TABLE `inventaire` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sites`
--

DROP TABLE IF EXISTS `sites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nom` varchar(50) NOT NULL,
  `ville` varchar(50) NOT NULL,
  `adresse` varchar(100) DEFAULT NULL,
  `type_site` enum('Siège','Entrepôt','Cross-dock') NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sites`
--

LOCK TABLES `sites` WRITE;
/*!40000 ALTER TABLE `sites` DISABLE KEYS */;
INSERT INTO `sites` VALUES (1,'Siège Social','Lille',NULL,'Siège'),(2,'WH1','Lens',NULL,'Entrepôt'),(3,'WH2','Valenciennes',NULL,'Entrepôt'),(4,'WH3','Arras',NULL,'Entrepôt'),(5,'CDK','Zone Saisonière',NULL,'Cross-dock');
/*!40000 ALTER TABLE `sites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transporteurs`
--

DROP TABLE IF EXISTS `transporteurs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transporteurs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nom_entreprise` varchar(100) NOT NULL,
  `contact_email` varchar(100) DEFAULT NULL,
  `statut_contrat` enum('Actif','Suspendu') DEFAULT 'Actif',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transporteurs`
--

LOCK TABLES `transporteurs` WRITE;
/*!40000 ALTER TABLE `transporteurs` DISABLE KEYS */;
INSERT INTO `transporteurs` VALUES (1,'Chrono Nord','logistique@chrononord.fr','Actif'),(2,'Fret Hauts-de-France','contact@frethdf.com','Actif'),(3,'Express Artois','exploitation@express-artois.fr','Actif');
/*!40000 ALTER TABLE `transporteurs` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-19 10:29:20
