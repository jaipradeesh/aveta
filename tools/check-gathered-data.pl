use strict;
use warnings;
use feature qw(say);

use Carp       qw(confess);
use Pod::Usage qw(pod2usage);
use File::Spec;

my @labels   = (0..6);
my $ok_tuple = {status => "ok"};

MAIN: {

    my $dirname = shift @ARGV or pod2usage();

    my %checks = (
        "label directories present" => \&_assert_label_dirs_present,
        "labeldir content check"    => \&_check_labeldir_contents,
    );

    while (my ($check_name, $check_func) = each %checks) {
        my $ret = $check_func->($dirname);
        say "$check_name: " . $ret->{status};
        if ($ret->{status} eq "error") {
            say "\t" . $ret->{error};
        }
    }

    _show_labeldir_stats($dirname);
}

sub _show_labeldir_stats {
    my $dirname = shift;

    my $total_count = 0;
    for my $label (@labels) {
        my $path = File::Spec->catfile($dirname, $label);
        confess "$path does not name a directory." unless (-d $path);
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
        say "$speedfile contains $count entries.";
    }
    say "Total count (per speedfiles): $total_count.";
}

sub _check_labeldir_contents {
    my $dirname = shift;
    my @errors;
    for my $label (@labels) {
        my $labeldir = File::Spec->catfile($dirname, $label);
        confess "$labeldir does not name a directory." unless(-d $labeldir);
        my $speedfile = File::Spec->catfile($labeldir, "speeds.txt");
        my $ret = _check_speedfile_contents($labeldir, $speedfile);
        push @errors, $ret->{error} if ($ret->{status} eq "error");
    }
    if (@errors) {
        return mkerr(join ";", @errors);
    }
    return $ok_tuple;
}

sub _check_speedfile_contents {
    my ($dirname, $speedfile) = @_;

    open my $in, "<:encoding(utf8)", $speedfile or
        confess "Could not open $speedfile for reading: $!";

    my @missing_files; # files present in the speedfile, but not in the dir.
    my %entry_counts;
    while (<$in>) {
        chomp;
        my ($filename, $lspeed, $rspeed) = split /,/;
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

sub _assert_label_dirs_present {
    my $dirname = shift;

    opendir my $dh, $dirname or
        confess "Could not open directory $dirname: $!";

    my %missing = map { $_ => 1 } @labels;
    while (readdir $dh) {
        next if (/^\./ || !/^\d+$/);
        delete $missing{$_};
    }

    closedir $dh;
    if (scalar keys %missing) {
        my $missing_dirs = join ",",
                                map { "'$_'" }
                                map { File::Spec->catfile($dirname, $_) }
                                keys %missing;
        return mkerr("Missing label directories: $missing_dirs");
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
