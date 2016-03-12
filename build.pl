#!/usr/bin/env perl

use strict;

use File::Find;

my %bundle_and_minify = (
    'js/pack.js' => (
        'js/main.js'
    ),
    'pack.css' => (
        'css/normalize.css',
        'css/main.css',
        'css/ir-sprites.css'
    ),
    'js/comic-pack.js' => (
        'js/dropdown.js',
        'js/single.js'
    ),
    'css/comic-pack.css' => (
        'css/dropdown.css',
        'css/single.css',
        'css/single-ir-sprites.css'
    )
);

print "Building ...\n";

$ENV{'JEKYLL_ENV'} = 'production';
system('bundle', 'exec', 'jekyll', 'build');


print "Minifying markup ...\n";

sub wanted {
    return unless /\.(html|xml|json)$/;
    local $/; # undef record separator: slurp mode
    my $f = $_;
    # Open and slurp.
    open(F, "<", $f) || die("$f: $!"); # chdir is on
    $_ = <F>;
    close(F);
    # Edit and overwrite.
    s/[ \n]+/ /g; # Replace multiple whitespace, including newline, with one space.
    s/[ ]+$//; # Remove trailing whitespace.
    open(F, ">", $f) || die("$f: $!");
    print F;
    close(F);
}

find(\&wanted, '_site');
