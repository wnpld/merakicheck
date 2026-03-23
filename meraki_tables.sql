CREATE DATABASE IF NOT EXISTS LibraryStatistics;

USE LibraryStatistics;

CREATE TABLE IF NOT EXISTS `LibraryBranches` (
  `BranchID` tinyint(3) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `BranchName` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `StreetAddress` varchar(30) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `City` varchar(15) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `ZIP` char(5) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `Phone` char(10) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL
);

CREATE TABLE IF NOT EXISTS `WirelessNetworks` (
  `WirelessID` tinyint(3) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `SSID` varchar(50) NOT NULL,
  `BranchID` tinyint(4) NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS `MerakiUniqueClients` (
  `MerakiClientID` int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `UIDHash` binary(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS `MerakiDailyConnections` (
  `MerakiConnectionID` int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `MerakiConnectionDate` date NOT NULL,
  `MerakiClientID` int(10) unsigned NOT NULL,
  `MerakiSessionCount` smallint(5) unsigned NOT NULL,
  `WirelessID` tinyint(3) unsigned NOT NULL,
  UNIQUE KEY `UniqueConnections` (`MerakiConnectionDate`,`MerakiClientID`,`WirelessID`),
  KEY `MerakiConnectionClients` (`MerakiClientID`),
  KEY `MerakiWireless` (`WirelessID`),
  CONSTRAINT `MerakiConnectionClients` FOREIGN KEY (`MerakiClientID`) REFERENCES `MerakiUniqueClients` (`MerakiClientID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `MerakiWireless` FOREIGN KEY (`WirelessID`) REFERENCES `WirelessNetworks` (`WirelessID`) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Optionally complete and uncomment this insert query with your library information
-- INSERT INTO LibraryBranches (BranchName, StreetAddress, City, ZIP, Phone) VALUES ('Main Library', '123 Main St.', 'Springfield', '12345', '1234567890'), ('Branch Library', '234 Spruce St.', 'Springfield', '12345', '1235678904');

-- Optionally complete and uncomment this insert query (as well as the above) with wireless network information
-- INSERT INTO WirelessNetworks (SSID, BranchID) VALUES ('LibraryHotspot', (SELECT BranchID FROM LibraryBranches WHERE BranchName = 'Main Library')), ('BranchHotspot', (SELECT BranchID FROM LibraryBranches WHERE BranchName = 'Branch Library'));
