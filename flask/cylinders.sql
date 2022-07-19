-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Jun 15, 2022 at 06:56 PM
-- Server version: 10.4.21-MariaDB
-- PHP Version: 7.4.29

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `cylinders`
--

-- --------------------------------------------------------

--
-- Table structure for table `Cylinder`
--

CREATE TABLE `Cylinder` (
  `_SID` varchar(17) NOT NULL,
  `batch_id` varchar(10) NOT NULL,
  `height` decimal(5,0) NOT NULL,
  `weight` decimal(5,0) NOT NULL,
  `dia` decimal(5,0) NOT NULL,
  `comp_str` decimal(3,0) NOT NULL,
  `frac_type` int(3) NOT NULL,
  `receiving_date` datetime(6) NOT NULL DEFAULT current_timestamp(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='cylinder analysis (density and compression)';

-- --------------------------------------------------------

--
-- Table structure for table `ticket`
--

CREATE TABLE `ticket` (
  `_batch_id` varchar(10) NOT NULL,
  `username` varchar(20) NOT NULL,
  `notes` varchar(200) NOT NULL,
  `client_name` varchar(50) NOT NULL,
  `site_add` varchar(150) NOT NULL,
  `struct_grid` varchar(150) NOT NULL,
  `charge_time` int(10) NOT NULL,
  `spec_air` int(5) NOT NULL,
  `mould_type` int(15) NOT NULL,
  `cast_by` varchar(25) NOT NULL,
  `temp_min` int(3) NOT NULL,
  `temp_max` int(3) NOT NULL,
  `mix_id` varchar(20) NOT NULL,
  `load_no` int(4) NOT NULL,
  `spec_slump` int(10) NOT NULL,
  `subclient_cont` varchar(50) NOT NULL,
  `cast_time` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  `meas_air` varchar(10) NOT NULL,
  `truck_no` int(10) NOT NULL,
  `ticket_no` varchar(15) NOT NULL,
  `agg_size` int(4) NOT NULL,
  `conc_supp` varchar(50) NOT NULL,
  `meas_slump` varchar(50) NOT NULL,
  `spec_str` varchar(10) NOT NULL,
  `conc_temp` decimal(3,0) NOT NULL,
  `amb_temp` decimal(3,0) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Ticket intake form table';

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `_username` varchar(20) NOT NULL,
  `password` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='SAFFA employee user data';

--
-- Indexes for dumped tables
--

--
-- Indexes for table `Cylinder`
--
ALTER TABLE `Cylinder`
  ADD PRIMARY KEY (`_SID`),
  ADD KEY `batch_id` (`batch_id`);

--
-- Indexes for table `ticket`
--
ALTER TABLE `ticket`
  ADD PRIMARY KEY (`_batch_id`),
  ADD KEY `username` (`username`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`_username`),
  ADD KEY `password` (`password`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `Cylinder`
--
ALTER TABLE `Cylinder`
  ADD CONSTRAINT `cylinder_ibfk_1` FOREIGN KEY (`batch_id`) REFERENCES `ticket` (`_batch_id`);

--
-- Constraints for table `ticket`
--
ALTER TABLE `ticket`
  ADD CONSTRAINT `ticket_ibfk_1` FOREIGN KEY (`username`) REFERENCES `user` (`_username`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
