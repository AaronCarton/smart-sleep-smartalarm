-- phpMyAdmin SQL Dump
-- version 4.6.6deb5ubuntu0.5
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: May 03, 2021 at 09:22 PM
-- Server version: 5.7.33-0ubuntu0.18.04.1
-- PHP Version: 7.2.24-0ubuntu0.18.04.7

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

DROP DATABASE IF EXISTS smartalarm;

CREATE DATABASE  IF NOT EXISTS `smartalarm` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `smartalarm`;

CREATE USER IF NOT EXISTS 'root_fswd'@'localhost' IDENTIFIED BY 'root_fswd';
GRANT ALL PRIVILEGES ON * . * TO 'root_fswd'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `smartalarm`
--

-- --------------------------------------------------------

--
-- Table structure for table `readings`
--

CREATE TABLE `readings` (
  `id` int(11) NOT NULL,
  `timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  `temp` float DEFAULT NULL,
  `light` float DEFAULT NULL,
  `sound` float DEFAULT NULL,
  `airquality` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `readings`
--

INSERT INTO `readings` (`id`, `timestamp`, `temp`, `light`, `sound`, `airquality`) VALUES
(1, '2014-02-27 06:25:57', 19.171, 79.26, 29, 45.4815),
(2, '1980-10-15 13:17:44', 21.5, 93.05, 60.27, 75.3133),
(3, '1983-07-16 08:23:54', 31.515, 2.4935, 60.45, 37.211),
(4, '1983-06-08 21:38:49', 22.647, 39.5924, 77.8439, 74.5347),
(5, '2000-11-14 19:57:45', 33.152, 18.452, 42.126, 84.0033),
(6, '1970-07-30 05:15:05', 31, 73.6793, 76.394, 61.5),
(7, '1988-05-09 05:30:02', 19.4104, 47.3609, 60.3732, 71.8),
(8, '1987-03-04 02:36:30', 19, 1.54, 73.19, 37),
(9, '2017-03-13 20:17:44', 33.6, 93.8029, 31.295, 51.4272),
(10, '1985-11-27 14:42:34', 20.1685, 30.3637, 31.389, 84),
(11, '1999-07-27 09:24:46', 29.6639, 7.545, 40.0597, 59),
(12, '2008-05-31 17:55:46', 27.7312, 73.5761, 25.1668, 66.7167),
(13, '2018-07-12 07:24:08', 29.278, 29.4121, 52.3782, 72.2364),
(14, '1972-04-09 01:52:37', 30.1, 14.6608, 68.8556, 84.9547),
(15, '1991-10-13 07:29:38', 34.254, 20.7589, 33.7456, 45.9),
(16, '1979-06-01 17:49:15', 14.7465, 37.5458, 63, 55),
(17, '1980-06-16 02:21:34', 32, 75.632, 51.1582, 66.291),
(18, '1983-01-20 14:18:18', 27.7, 69.1091, 31.96, 69.74),
(19, '2014-03-31 23:56:01', 29.2143, 75.9336, 56.9194, 35.8653),
(20, '1986-05-09 08:30:35', 19.5, 99.2002, 30.3411, 66),
(21, '1993-09-10 03:14:45', 31.9702, 72.1, 32.0945, 37.5775),
(22, '2003-03-10 15:35:18', 16, 81.751, 33.1, 49.6419),
(23, '1993-02-17 15:23:53', 25.3, 1.5945, 45, 77.7077),
(24, '2015-01-01 00:21:22', 27.5484, 62.805, 39.4031, 71.8413),
(25, '1989-10-03 04:10:06', 18.0636, 97.0981, 74.1, 47.75),
(26, '2009-04-08 21:57:50', 16.2215, 68.007, 72.7423, 35.4436),
(27, '2012-12-04 07:04:07', 17.3142, 31.7654, 66.669, 71.53),
(28, '1996-11-21 22:06:13', 11.1969, 48.95, 42.8555, 43.0992),
(29, '1977-03-17 21:32:27', 29.6, 34.99, 47.4651, 66.588),
(30, '1998-11-19 08:06:29', 25.28, 94.757, 51.434, 78.6327);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `readings`
--
ALTER TABLE `readings`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `timestamp` (`timestamp`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `readings`
--
ALTER TABLE `readings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
