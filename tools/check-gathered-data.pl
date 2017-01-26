use strict;
use warnings;
use feature qw(say);

use Carp       qw(confess);
use Pod::Usage qw(pod2usage);
use File::Spec;

my $ok_tuple = {status => "ok"};

MAIN: {

    my $dirname = shift @ARGV or pod2usage();

    my %checks = (
        "speedfile content check"    => \&_check_speedfile_contents,
    );

    while (my ($check_name, $check_func) = each %checks) {
        my $ret = $check_func->($dirname);
        say "$check_name: " . $ret->{status};
        if ($ret->{status} eq "error") {
            say "\t" . $ret->{error};
        }
    }

    _show_stats($dirname);
}

sub _is_img_filename {
    my $filename = shift;
    my ($extn)   = ($filename =~ /\.([^.]+)$/);
    return $extn && ($extn =~ /^(?:jpg|jpeg|png|bmp)$/i);
}

sub _show_stats {
    my $path = shift;

    my $total_count      = 0;
    my $total_file_count = 0;

    my $speedfile = File::Spec->catfile($path, "speeds.txt");
    confess "$speedfile does not name a file." unless (-f $speedfile);

    my $count = do {
        open my $in, "<:encoding(utf8)", $speedfile or
            confess "Could not open $speedfile for reading: $!";
        my $ctr = 0;
        $ctr++ while (<$in>);
        close $in;
        $ctr;
    };
    $total_count += $count;

    my $file_count = do {
        opendir my $dh, $path or confess "Could not open directory $path: $!";
        my $ctr = 0;
        while (readdir $dh) {
            next if (/^\./ || 
                     !-f File::Spec->catfile($path, $_) ||
                     !_is_img_filename($_));
            ++$ctr;
        }
        closedir $dh;
        $ctr;
    };
    if ($file_count == $count) {
        say "Total $count examples in $path.";
    } else {
        say "error: there are $count examples as per speedfile, but ".
            "$file_count files in $path.";
    }
}

sub _check_speedfile_contents {
    my $dirname = shift;

    my $speedfile = File::Spec->catfile($dirname, "speeds.txt");
    open my $in, "<:encoding(utf8)", $speedfile or
        confess "Could not open $speedfile for reading: $!";

    my @missing_files; # files present in the speedfile, but not in the dir.
    my %entry_counts;
    while (<$in>) {
        chomp;
        my ($filename, $lspeed, $rspeed, $lspeed_aft, $rspeed_aft) = split /,/;
        my $path = File::Spec->catfile($dirname, $filename);
        push @missing_files, $filename unless (-f $path);
        $entry_counts{$filename}++;
    }
    close $in;

    my @errors;
    my $missing_files_msg =
        "These files are missing in $dirname, but named in $speedfile: ";
    my $repeated_files_msg =
        "These files are repeated in $speedfile at least once: ";

    my %msg_val_map = (
        $missing_files_msg  => \@missing_files,
        $repeated_files_msg => [grep {$entry_counts{$_} > 1} keys %entry_counts],
    );
    while (my ($msg, $vals) = each %msg_val_map) {
        push @errors, _err_msg_csv($msg, @$vals) if (@$vals);
    }
    if (@errors) {
        return mkerr(join ";", @errors);
    }
    return $ok_tuple;
}

sub mkerr {
    my $msg = shift;
    return {
        status => "error",
        error  => $msg,
    };
}

sub _err_msg_csv {
    my ($msg, @vals) = @_;
    return $msg . join(",", @vals);
}

__END__

=pod

=head1 NAME

check-gathered-data.pl

=head1 SYNOPSIS

    perl check-gathered-data.pl DIRNAME

=head1 DESCRIPTION

Check Aveta training data and print diagnostics.


=cut
