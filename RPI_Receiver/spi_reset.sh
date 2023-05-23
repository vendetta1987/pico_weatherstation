#!/bin/bash
rmmod spi_bcm2835
rmmod spidev
modprobe spi_bcm2835
modprobe spidev

