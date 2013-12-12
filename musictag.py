# -*- coding: utf-8 -*-

from __future__ import division

import fnmatch
import os
import re
import eyeD3
from eyeD3.tag import TagException
import shutil
import traceback
import sys

import utils

#music_dir = "/media/store n go 500/myMusic"
#output_music_dir = "/media/store n go 500/myMusic_clean"
music_dir = "/media/0AF2DB962B0F4DD3/music"
#music_dir = "/media/F69829B798297771/myMusic_clean/untagged"
#music_dir = "/media/323C9A693C9A27BD/myMusic/Bijelo Dugme"
output_music_dir = "/media/0AF2DB962B0F4DD3/music_clean"
#output_music_dir = "/media/F69829B798297771/myMusic_clean2"
#output_music_dir = "/media/F69829B798297771/myMusic_clean3"
#output_music_dir = "/tmp/music"

rules = ('AC-DC',
         'V.I.P',
         'The XX',
         '121 Greatest Rock&Roll Songs')

acronymns = ('MTV','TBF','ET','LMFAO','AFI','UB40','II','CD','OMD','DMX','DJ','MVP','VCR')

compilations = (u'The Very Best Of MTV Unplugged',
                u"Grey's Anatomy Soundtrack Vol. 2",
                u"Greys Anatomy Soundtrack Vol.3",
                u'101 Running Songs',
                u'101 Running Songs Lap 2',
                u'This Is Dubstep 2011 (Presented By GetDarker)',
                u'121 Greatest Rock&Roll Songs',
                u'Antologija Omis',
                u'Ajmo Bili',
                u'Navijačke',
                u'Najlipše Hajdukove Pisme',
                u'The Best Of 90 S Dance Hits (r',  #TODO - rename this eventually
                u'Libar I - Da Te Mogu Pismom Zvati 2005',
                u'Libar II - Da Te Mogu Pismom Zvati 2005',
                u'Kill Bill (soundtrack) (vol.1)',
                u'Kill Bill (soundtrack) (vol.2)',
                u'Jungle Sound Gold / CD 1',
                u'Jungle Sound Gold / CD 2',
                u'Sick Music') 

artists = (u'Djordje Balašević',
           u'Željko Joksimović',
           u'Zoran Mišić',
           u'Opća Opasnost',
           u'Zabranjeno Pušenje',
           u'Atomsko Sklonište',
           u'Milo Hrnić',
           u'Miroslav Škoro',
           u'Sanja Ðordević',
           u'Oliver Dragojević',
           u'Dječaci',
           u'Mišo Kovač',
           u'Dražen Zečić')

ignore_albums = ('mymusic',
                 'www.domaci.de',
                 'unknown album (02/01/2006 13.45.02)',
                 'www.yucafe.com',
                 'http://www.homeofmusic.com')

def find_music_paths(root_dir,force=False):

    music_paths = []
    other_paths = []
    
    for root, dirnames, filenames in os.walk(root_dir):
        subroot = root[len(root_dir):].lstrip('/').split('/')[0]
        
        if subroot not in ('artists','compilations','corrupt','other') or force:
        
            matched_filenames = fnmatch.filter(filenames, '*.[mM][pP]3')
                               #fnmatch.filter(filenames, '*.[mM]4[aA]')
            
            #matched_filenames = fnmatch.filter(filenames, '*Our Lives*')
            
            #if 'Elemental' in root:
            #    matched_filenames = fnmatch.filter(filenames, '*.[mM][pP]3')
            #else:
            #    matched_filenames = []
            
            unmatched_filenames = set(filenames) - set(matched_filenames)
            music_paths.extend([os.path.join(root,o) for o in matched_filenames])
            other_paths.extend([os.path.join(root,o) for o in unmatched_filenames])

    other_extensions = set([utils.extension(o) for o in other_paths])
    if other_extensions:
        print 'warning - found other file types: ',other_extensions
    return (music_paths,other_paths)

artists_rmpalats = tuple([utils.rmpalat(a).lower() for a in artists])
rules_lower = tuple([r.lower() for r in rules])

def mkpath(_dir,artist,album,track,name,tag,compilation=False):
    ext = utils.extension(tag.linkedFile.name)

    if compilation:
        filename = artist+' - '+(album+' - ' if album is not None else '')+(unicode(track)+' - ' if track is not None else '')+name+"."+ext
        args = ('compilations',album,filename)
    else:
        filename = artist+' - '+(album+' - ' if album is not None else '')+(unicode(track)+' - ' if track is not None else '')+name+"."+ext
        args = ('artists',artist,album,filename) if album else ('artists',artist,filename)
    
    args = utils.correct_path(args)
    return os.path.join(_dir,*args)

def clean_word(word):
    if word.upper() in acronymns:
        word = word.upper()
    else:
        word = word.lower().capitalize()
    return word

def link_tag(_file):
    tag = eyeD3.Tag()
    v2_failed = False
    
    try:
        tag.link(_file,eyeD3.ID3_V2)
        if not (tag.getArtist() and tag.getTitle()):
            v2_failed = True
    except TagException:
        print 'warning: failed to load ID3_V2 tag'
        traceback.print_exc(file=sys.stdout)
        v2_failed = True
        
    if v2_failed:
        tag.link(_file,eyeD3.ID3_V1)
    return tag

def update_tag(_file,**kwargs):
    tag = link_tag(_file)
    
    #tag.setVersion(eyeD3.ID3_V2_4)
    #tag.remove()

    #if tag.isV1() or tag.getVersion()!=eyeD3.ID3_V2_4:
    tag.setVersion(eyeD3.ID3_V2_4)
    tag.remove(eyeD3.ID3_V1)
    #print 'converting to ID3_V2_4 - ',_file

    tag.removeComments()
    tag.removeLyrics()
    tag.removeImages()
    
    tag.setTextEncoding(eyeD3.UTF_8_ENCODING)

    for (k,v) in kwargs.items():
        getattr(tag,'set'+k.capitalize())(v if v is not None else "")
    tag.update()

def capitalize_all(value):
    return ' '.join([clean_word(p) for p in re.split('\\s+',value)])

def cleanup(artist):
    if artist is not None:
        artist = artist.strip().strip("/").strip().lower()

        try:
            rule_index = rules_lower.index(artist)
        except ValueError:
            rule_index = -1

        if rule_index != -1:
            artist = rules[rule_index]
        else:
            try:
                artist_palat_index = artists_rmpalats.index(utils.rmpalat(artist).lower())
            except ValueError:
                artist_palat_index = -1

            if artist_palat_index != -1:
                artist = artists[artist_palat_index]
            else:
                artist = capitalize_all(artist)
    return artist

def guess_tags_from_filename(_file):

    artist = None
    album = None
    name = None
    track = None

    (_dir,filename) = os.path.split(_file)

    m = re.match('^\s*([A-Za-z][^-]+)\s*-\s*([^-]+)\s*\.\w+$',filename)
    if m:
        artist = unicode(m.group(1),'utf-8')
        name = unicode(m.group(2),'utf-8')

    #look for album dir
    if _dir != music_dir:
        dirname = os.path.split(_dir)[1]
        album = unicode(dirname,'utf-8')

    return (artist,album,name,track)

if __name__ == "__main__":
    
    force = False
    force_move = True
    copy_others = True
    
    shutil.rmtree(output_music_dir,ignore_errors=True)
    (in_size,in_files) = utils.dir_size(music_dir)
    
    (music_paths,other_paths) = find_music_paths(music_dir,force)
    
    if not force and not force_move:
        print 'copying artists'
        shutil.copytree(os.path.join(music_dir,'artists'),os.path.join(output_music_dir,'artists'))
        print 'copying compilations'
        shutil.copytree(os.path.join(music_dir,'compilations'),os.path.join(output_music_dir,'compilations'))
        print 'copying corrupt'
        shutil.copytree(os.path.join(music_dir,'corrupt'),os.path.join(output_music_dir,'corrupt'))
        print 'copying other'
        shutil.copytree(os.path.join(music_dir,'other'),os.path.join(output_music_dir,'other'))
    elif not force and force_move:
        print 'moving artists'
        shutil.move(os.path.join(music_dir,'artists'),os.path.join(output_music_dir,'artists'))
        print 'moving compilations'
        shutil.move(os.path.join(music_dir,'compilations'),os.path.join(output_music_dir,'compilations'))
        print 'moving corrupt'
        shutil.move(os.path.join(music_dir,'corrupt'),os.path.join(output_music_dir,'corrupt'))
        print 'moving other'
        shutil.move(os.path.join(music_dir,'other'),os.path.join(output_music_dir,'other'))
        
    if copy_others:
        for other_path in other_paths:
            extension = utils.extension(other_path)
            (basename,filename) = os.path.split(other_path)
            music_file_output = os.path.join(output_music_dir,'other',extension,basename[len(music_dir)+1:],filename)
            music_file_output = music_file_output.replace('/other/%s/other/%s' % (extension,extension),'/other/%s'% (extension,))
            utils.copy(other_path,music_file_output)
            print 'output: %s' % (music_file_output,)
    
    corrupt_music_paths = []
    missing_tags_paths = []
    guessed_missing_tags_paths = []
    
    #music_paths = list(reversed(music_paths))
    #music_paths = music_paths[:30]
    
    for (i,music_file) in enumerate(music_paths):
        
        retry = 5
        
        while True:
            print ''    
            print '*'*100
            print '#%d' % i
            print 'input: %s' % (music_file,)
        
            try:
                tag = link_tag(music_file)
        
                is_guess = False
                is_complilation = False
                
                artist = tag.getArtist()
                album = tag.getAlbum()
                track = int(tag.getTrackNum()[0]) if tag.getTrackNum()[0] is not None else None
                title = tag.getTitle()
                
                print 'orig tags:'
                print '\tartist: %s' % artist
                print '\talbum: %s' % album
                print '\ttrack: %s' % track
                print '\ttitle: %s' % title
                
                artist = artist.strip() if artist is not None and artist.strip() else None
                album = album.strip() if album is not None and album.strip() else None
                title = title.strip() if title is not None and title.strip() else None
                
                if album is not None:
                    if album.lower() in ignore_albums:
                        print 'warning: album in ignored_albums'
                        album = None
                    elif album == '':
                        album = None
                if album is None and track is not None:
                    print 'warning: track no. defined without album'
                    track = None
        
                if artist is None or title is None:
                    if retry:
                        retry-=1
                        continue
        
                    (_artist,_album,_title,_track) = guess_tags_from_filename(music_file)
                    
                    print 'guessed tags:'
                    print '\tartist: %s' % _artist
                    print '\talbum: %s' % _album
                    print '\ttrack: %s' % _track
                    print '\ttitle: %s' % _title
                    
                    if (artist is not None or _artist is not None) and (title is not None or _title is not None):
                        is_guess = True
                        artist = artist if artist is not None else _artist
                        album = album if album is not None else _album
                        title = title if title is not None else _title
                        track = track if track is not None else _track
                    else:
                        missing_tags_paths.append(music_file)
                        print 'warning: unable to guess tags'
                        music_file_output = os.path.join(os.path.join(output_music_dir,'untagged',music_file[len(music_dir)+1:]))
                        utils.copy(music_file,music_file_output)
                        print 'output: %s' % (music_file_output,)
                        #print 'UNTAGGED!'
                        #exit()
                        break
        
                artist = cleanup(artist)
                album = cleanup(album)
                title = cleanup(title)
                
                is_compilation = album in compilations
                music_file_output = mkpath(output_music_dir,artist,album,track,title,tag,is_compilation)
                
                utils.copy(music_file,music_file_output)
                update_tag(music_file_output,artist=artist,album=album,title=title)
                
                print 'updated tags:'
                print '\tartist: %s' % artist
                print '\talbum: %s' % album
                print '\ttrack: %s' % track
                print '\ttitle: %s' % title
                
                print 'compilation: ',is_compilation
                print 'guessed: ',is_guess
                print 'output: %s' % (music_file_output,)
        
                if is_guess:
                    guessed_missing_tags_paths.append(music_file_output)
                    
            except Exception,e:
                #print 'error: ',repr(e)
                print 'error: '
                traceback.print_exc(file=sys.stdout)
                corrupt_music_paths.append(music_file)
                music_file_output = os.path.join(output_music_dir,'corrupt',os.path.split(music_file)[1])
                utils.copy(music_file,music_file_output)
                print 'output: %s' % (music_file_output,)
            break
    
    print '\n# music_files:',len(music_paths)
    
    if copy_others and other_paths:
            print '\other_paths (#%d):' % len(other_paths)
            print '\n'.join(other_paths)
    
    if corrupt_music_paths:
        print '\ncorrupt_music_files (#%d):' % len(corrupt_music_paths)
        print '\n'.join(corrupt_music_paths)
    
    if missing_tags_paths:
        print '\nmissing_tags_music_files (#%d):' % len(missing_tags_paths)
        print '\n'.join(missing_tags_paths)
    
    if guessed_missing_tags_paths:
        print '\nguessed_missing_tags_files (#%d):' % len(guessed_missing_tags_paths)
        print '\n'.join(guessed_missing_tags_paths)
    
    (out_size,out_files) = utils.dir_size(output_music_dir)
    
    print 'size %s(#%d) -> %s(#%d) (%.2f%%)' % (utils.humanize_bytes(in_size,2),
                                                in_files,
                                                utils.humanize_bytes(out_size,2),
                                                out_files,
                                                (out_size-in_size)/in_size*100 if in_size else 0)
