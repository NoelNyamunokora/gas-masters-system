-- Gas Masters Database Export
-- Generated: 2026-03-24 23:06:44
-- WARNING: This file contains sensitive data. Keep it secure!

SET FOREIGN_KEY_CHECKS=0;

-- Table: depot_allocations
DROP TABLE IF EXISTS `depot_allocations`;
CREATE TABLE `depot_allocations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `depot_id` int NOT NULL,
  `amount` float NOT NULL,
  `allocation_date` datetime DEFAULT NULL,
  `allocated_by` int NOT NULL,
  `notes` text,
  PRIMARY KEY (`id`),
  KEY `depot_id` (`depot_id`),
  KEY `allocated_by` (`allocated_by`),
  CONSTRAINT `depot_allocations_ibfk_1` FOREIGN KEY (`depot_id`) REFERENCES `depots` (`id`),
  CONSTRAINT `depot_allocations_ibfk_2` FOREIGN KEY (`allocated_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table: depots
DROP TABLE IF EXISTS `depots`;
CREATE TABLE `depots` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `location` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `current_inventory` float DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC;

-- Data for table: depots
INSERT INTO `depots` (`id`, `name`, `location`, `current_inventory`, `created_at`) VALUES
(10, 'Damofalls Depot', 'Damofalls Ruwa ', 3973.0, '2026-03-22 13:55:44');

-- Table: purchases
DROP TABLE IF EXISTS `purchases`;
CREATE TABLE `purchases` (
  `id` int NOT NULL AUTO_INCREMENT,
  `amount` float NOT NULL,
  `purchase_date` datetime DEFAULT NULL,
  `supplier` varchar(100) DEFAULT NULL,
  `cost` float DEFAULT NULL,
  `notes` text,
  `created_by` int NOT NULL,
  `price_per_kg` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `purchases_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table: transactions
DROP TABLE IF EXISTS `transactions`;
CREATE TABLE `transactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `depot_id` int NOT NULL,
  `filler_id` int NOT NULL,
  `amount_dispensed` float NOT NULL,
  `transaction_date` datetime DEFAULT NULL,
  `notes` text,
  `price_per_kg` float NOT NULL DEFAULT '0',
  `total_amount` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `depot_id` (`depot_id`),
  KEY `filler_id` (`filler_id`),
  CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`depot_id`) REFERENCES `depots` (`id`),
  CONSTRAINT `transactions_ibfk_2` FOREIGN KEY (`filler_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table: users
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(80) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(20) NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `approved_at` datetime DEFAULT NULL,
  `approved_by` int DEFAULT NULL,
  `assigned_depot_id` int DEFAULT NULL,
  `first_name` varchar(50) NOT NULL DEFAULT 'First',
  `surname` varchar(50) NOT NULL DEFAULT 'Name',
  `phone_number` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `phone_number` (`phone_number`),
  UNIQUE KEY `phone_number_2` (`phone_number`),
  KEY `approved_by` (`approved_by`),
  KEY `assigned_depot_id` (`assigned_depot_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`approved_by`) REFERENCES `users` (`id`),
  CONSTRAINT `users_ibfk_2` FOREIGN KEY (`assigned_depot_id`) REFERENCES `depots` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Data for table: users
INSERT INTO `users` (`id`, `username`, `password_hash`, `role`, `status`, `created_at`, `approved_at`, `approved_by`, `assigned_depot_id`, `first_name`, `surname`, `phone_number`) VALUES
(1, 'admin', 'pbkdf2:sha256:600000$qCw30LH6ie4UN3aO$aa975b39919f5b0e6057b1ed99abdf1be1335814188f66755e1a5211116b5173', 'manager', 'active', '2026-03-16 14:02:29', '2026-03-16 14:02:29', NULL, NULL, 'Noel', 'Nyamunokora', '+00000000001'),
(3, 'operator1', 'pbkdf2:sha256:600000$prvMdkgcPXhaVhSA$274030097496e1dc82ea6b75c452bfef343ad43060f5d567c6c924274e775573', 'filler', 'active', '2026-03-18 10:13:30', '2026-03-24 15:19:50', 1, 10, 'Noel ', 'Nyamunokora', '+263784158452');

SET FOREIGN_KEY_CHECKS=1;
