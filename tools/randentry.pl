# Given a speedfile, output a random line, but with the output speeds omitted.
# In other words, output only filename (absolute), lspeed and rspeed.
use strict;
use warnings;
use feature qw(say);
use Data::Dumper;

use File::Spec;
use File::Slurp qw(read_file);

my $speedfile = shift @ARGV or die "Need speedfile.";

my (undef, $dir, $file) = File::Spec->splitpath($speedfile);

$dir //= ".";

my @lines = read_file($speedfile);

chomp for @lines;

my $rand_index = int(rand(scalar @lines));

my ($filename, $lspeed, $rspeed) = split /,/, $lines[$rand_index];

my $absfile = File::Spec->catfile($dir, $filename);

say "$absfile,$lspeed,$rspeed";


