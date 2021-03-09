_USE_THREAD = True
##@mainpage Introduction
#Qub is a low level library, in it you can find different tools separate
#in sub section
#
#@section examples Examples
#In this section you'll find some simple example of how to use Qub library
#@see Qub::Examples
#@see howto
#
#@section widget Widget
#In this sub directory, you will find some simple widgets and some specific dedicate to
#Image data handling
#@see Qub::Widget
#
#@subsection graph Graph
#This directory is dedicate to graph tool.
#@see Qub::Widget::Graph
#
#@subsection datasource DataSource
#In this section you'll find some widget which display source classes
#i.e: all the datas which can be handle by Qub (for now Qub can only handle image array)
#@see Qub::Widget::DataSource
#@see Qub::Data::Class
#
#@section object Objects
#Here, it's all low level objects of the Qub library.
#@see Qub:Objects
#
#@section print Print
#tools to display print preview and print
#@see Qub::Print
#
#@section plugins Plugins
#mother class of Oxidis plugins
#@see Qub::Plugins
#
#@section icons icons
#Icon's library used by Qub
#
#@section tools Tools
#simple tools
#@see Qub::Tools
#
#@section ctools CTools
#This is all compiled library module.
#@see Qub::CTools
#

##@brief disable thread in the Qub library
#
#This methode must be called before import of QubThreads
def disableThread() :
    global _USE_THREAD
    _USE_THREAD = False

def useThread() :
    return _USE_THREAD

