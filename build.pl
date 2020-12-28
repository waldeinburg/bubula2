#!/usr/bin/perl

use strict;
use warnings;

use Getopt::Long;
use File::Find;
use File::Basename;
use Cwd;
use YAML::XS;

use constant SITE_DIR => '_site';
use constant YUICOMPRESSOR => '/usr/local/share/yuicompressor-2.4.8.jar';
use constant PRIVATE => 'private.yml';

my %bundle_and_minify = (
    'js/pack.js' => [
        'js/main.js'
    ],
    'css/pack.css' => [
        'css/normalize.css',
        'css/main.css',
        'css/ir-sprites.css'
    ],
    'js/comic-pack.js' => [
        'js/dropdown.js',
        'js/comic.js'
    ],
    'css/comic-pack.css' => [
        'css/dropdown.css',
        'css/comic.css',
        'css/comic-ir-sprites.css'
    ]
);


my $nobuild = 0;
my $nominify = 0;
my $nobundle = 0;
my $keeporigs = 0;
my $deploy = 0;

GetOptions(
    'nobuild'   => \$nobuild,
    'nominify'  => \$nominify,
    'nobundle'  => \$nobundle,
    'keeporigs' => \$keeporigs,
    'deploy'    => \$deploy
) || exit;


unless ($nobuild) {
    print "Building ...\n";

    $ENV{'JEKYLL_ENV'} = 'production';
    system('bundle', 'exec', 'jekyll', 'build') && die("Build error!");
}

unless ($nominify) {
    print "Minifying markup ...\n";

    sub wanted {
        return unless /\.(html|xml|json)$/;
        local $/; # undef record separator: slurp mode
        my $f = $_;
        # Open and slurp.
        open(F, '<', $f) || die("$File::Find::name: $!"); # chdir is on
        $_ = <F>;
        close(F);
        # Edit and overwrite.
        s/[ \n]+/ /g; # Replace multiple whitespace, including newline, with one space.
        s/[ ]+$//; # Remove trailing whitespace.
        open(F, '>', $f) || die("$File::Find::name: $!");
        print F;
        close(F);
    }

    find(\&wanted, SITE_DIR);
}

unless ($nobundle) {
    print "Bundling and minifying JS and CSS ...\n";

    local $/;
    my $cwd = getcwd;
    chdir(SITE_DIR) || die("Could not switch to " . SITE_DIR);

    for my $pack (keys %bundle_and_minify) {
        my($name, $dir, $suffix) = fileparse($pack, qr/\.[^.]+/);
        my $minpack = "$dir$name.min$suffix";

        open(P, '>', $pack) || die("$pack: $!");
        for my $f (@{$bundle_and_minify{$pack}}) {
            open(F, '<', $f) || die("$f: $!");
            $_ = <F>;
            print P;
            close(F);
            unlink($f) unless $keeporigs;
        }
        close(P);

        system('java', '-jar', YUICOMPRESSOR, '-v', '-o', $minpack, '--charset', 'utf-8', $pack)
            && die("Failed execute: $!");
        unlink($pack) unless $keeporigs;
    }

    chdir($cwd) || die("Could not switch back to workdir!");
}

if ($deploy) {
    print "Deploying ...\n";
    open(F, '<', PRIVATE) || die(PRIVATE . ": $!");
    local $/;
    my $conf = Load(<F>);
    close(F);
    my $server = $conf->{server};
    my $wwwdir = $conf->{wwwdir};

    sub exec_ssh {
        my ($cmd) = @_;
        system('ssh', $server, $cmd)
            && die("Could not execute ssh command $cmd");
    }

    # Commented out. Current host does not support rsync.
    # system('rsync', '-avuz', '--delete',
    #     SITE_DIR . '/',
    #     $server . ':' . $wwwdir . '/'
    # );

    system('./remote_sync.sh', SITE_DIR, $server, $wwwdir);
}
