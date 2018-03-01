"""
 Lib_affinity.py
 
 This python library cointains tools and functions to analyse kmp_affinity verbose outputs.
 It makes it easier to understand kmp_affinity outputs by providing a simpler summary
 
"""

# ______________________________________________________________________________
# Class Affinity

class Affinity:
  """
  ______________________________________________________________________________  
    
  Class Affinity
  
  Enable to build affinity properties
  ______________________________________________________________________________  
  """
  def __init__(self):
    self.info_dict = {}   # Dictionary containing the kmp affinity information sorted by info number
    self.nlines = 0       # Number of lines or infos
    
    self.package_list = []   # List of packages
    self.npackages = 0       # Number of packages

  def sort_by_info_number(self,file_content):
    """
    Create a dictionary containing the different line of the kmp affinity output
    Entries of the disctionary are the affinity info numbers and the content the message of the line
    Input:
    - file_content: list of lines (string) to be analysed
    """
    for i in range(self.nlines):
      line = file_content[i]
      if (line[0:3] == 'OMP'):
        info_num = line[11:14]
        if info_num in self.info_dict:
          self.info_dict[info_num].append(line[30:].rstrip())
        else:
          self.info_dict[info_num] = []
          self.info_dict[info_num].append(line[30:].rstrip())
    
    # Merging of different numbers
    if '159' in self.info_dict:
      self.info_dict['179'] = self.info_dict['179'] + self.info_dict['159']

  def get_packages(self):
    """
    Get the number of package, number of cores and threads
    Initialize the package list
    
    ____________________________________________________________________________      
    """
    self.npackages = len(self.info_dict['179'])
    print (' Number of packages:',self.npackages)
    for i in range(self.npackages):
      info = self.info_dict['179'][i]
      # get number of cores
      ncores = int(info.split('x')[1].split(' ')[1])
      
      # get number of threads per cores
      nthreads = int(info.split('x')[2].split(' ')[1])
          
      package = Package(nthreads=nthreads)
      self.package_list.append(package)
      print(' Package %d'%i,'number of cores:',ncores,'number of threads:',nthreads)

  def get_initial_proc_set(self):
    """
    Get the proc set and associate it to the packages
    """
    for i in range(len(self.info_dict['154'])):
      info = self.info_dict['154'][i]
      self.package_list[i].proc_list = info.split(' ')[5][1:-1].split(',')
      for j in range(len(self.package_list[i].proc_list)):
        self.package_list[i].proc_list[j] = int(self.package_list[i].proc_list[j])
      print
      print(' Package %d'%i,' list of proc set:',self.package_list[i].proc_list)
      self.package_list[i].proctocore_list = [None]*len(self.package_list[i].proc_list)
      self.package_list[i].proctothread_list = [None]*len(self.package_list[i].proc_list)

  def get_proc_map(self):
    """
    Create the proc map, with the core and physical thread ids as given by the kmp affinity
    """
    info_list = self.info_dict['171']
    for i in range(len(info_list)):
      infos = info_list[i].split(' ')
      procnum = int(infos[2])
      ip = int(infos[6])
      ic = int(infos[8])
      if (len(infos)>9): 
        it = int(infos[10])
      else:
        it = 0

      i = 0
      while(i<self.npackages):
        if (procnum in self.package_list[i].proc_list):
          iproc = self.package_list[i].proc_list.index(procnum)
          if (ic in self.package_list[i].coreid_list):
            k = self.package_list[i].coreid_list.index(ic)
          else:
            self.package_list[i].add_core(ic,nthreads=self.package_list[i].nthreads)
            k = self.package_list[i].coreid_list.index(ic)
          self.package_list[i].proctocore_list[iproc] = k
          self.package_list[i].core_list[k].update_thread(it,pthread_id=procnum)
          self.package_list[i].proctothread_list[iproc] = it
          i = self.npackages
        i+=1
      #self.package_list[ip].core_list
      
  def get_thread_bindings(self):
    """
    Get how logical threads are bound to physical threads
    """

    # 242 does not contain tid
    if '242' in self.info_dict:
      info_list = self.info_dict['242']
      for i in range(len(info_list)):
        infos = info_list[i].split(' ')
        pid = int(infos[1])
        lthread_id = int(infos[3])
      
        proc_set = infos[9][1:-1].split(',')
        for ips in range(len(proc_set)):
          procnum = int(proc_set[ips])
          ip = 0
          while(ip<self.npackages):
            if (procnum in self.package_list[ip].proc_list):
              k = self.package_list[ip].proc_list.index(procnum)
              ic = self.package_list[ip].proctocore_list[k]
              it = self.package_list[ip].proctothread_list[k]
              self.package_list[ip].core_list[ic].thread_list[it].lthread_pid = pid
              self.package_list[ip].core_list[ic].thread_list[it].lthread_id = lthread_id
            ip+=1

    if '247' in self.info_dict:
      info_list = self.info_dict['247']
      for i in range(len(info_list)):
        infos = info_list[i].split(' ')
        pid = int(infos[1])
        tid = int(infos[3])
        lthread_id = int(infos[5])
      
        proc_set = infos[11][1:-1].split(',')
        for ips in range(len(proc_set)):
          procnum = int(proc_set[ips])
          ip = 0
          while(ip<self.npackages):
            if (procnum in self.package_list[ip].proc_list):
              k = self.package_list[ip].proc_list.index(procnum)
              ic = self.package_list[ip].proctocore_list[k]
              it = self.package_list[ip].proctothread_list[k]
              self.package_list[ip].core_list[ic].thread_list[it].lthread_pid = pid
              self.package_list[ip].core_list[ic].thread_list[it].lthread_tid = tid
              self.package_list[ip].core_list[ic].thread_list[it].lthread_id = lthread_id
            ip+=1
 
          
  
  def show(self):
    """
    Output the summary in the terminal
    ____________________________________________________________________________    
    """
    indent1 = '  '
    indent2 = indent1 + indent1
    for ip in range(self.npackages):
      print(' Package %d'%ip)
      for ic in range(self.package_list[ip].ncores):
        print(' ' + indent1 + 'Core %d'%ic,'id:',self.package_list[ip].coreid_list[ic])
        for it in range(self.package_list[ip].core_list[ic].nthreads):
          pthread_id = self.package_list[ip].core_list[ic].thread_list[it].pthread_id
          lthread_pid = self.package_list[ip].core_list[ic].thread_list[it].lthread_pid
          lthread_tid = self.package_list[ip].core_list[ic].thread_list[it].lthread_tid
          lthread_id = self.package_list[ip].core_list[ic].thread_list[it].lthread_id
          print(' ' + indent2 + ' - Thread %d'%it + ' - proc #%d - pid %d - tid %d - logical thread #%d'%(pthread_id,lthread_pid,lthread_tid,lthread_id))
      print('')  
  
  def output_in_file(self,output_filename):   
    """
    Output the summary in a file
    ____________________________________________________________________________    
    """
   
    indent1 = '  '
    indent2 = indent1 + indent1  
    output_file = open(output_filename, "w")
    
    for i in range(self.npackages):          
      output_file.write(' Package %d, number of cores: %d, number of threads: %d'%(i,self.package_list[i].ncores,self.package_list[i].nthreads))    
    
    for ip in range(self.npackages):
      output_file.write(' \n')
      output_file.write(' Package %d \n'%ip)
      for ic in range(self.package_list[ip].ncores):
        output_file.write(' ' + indent1 + 'Core %d - id: %d \n'%(ic,self.package_list[ip].coreid_list[ic]))
        for it in range(self.package_list[ip].core_list[ic].nthreads):
          pthread_id = self.package_list[ip].core_list[ic].thread_list[it].pthread_id
          lthread_pid = self.package_list[ip].core_list[ic].thread_list[it].lthread_pid
          lthread_tid = self.package_list[ip].core_list[ic].thread_list[it].lthread_tid
          lthread_id = self.package_list[ip].core_list[ic].thread_list[it].lthread_id
          output_file.write(' ' + indent2 + ' - Thread %d'%it + ' - proc #%d - pid %d - tid %d - logical thread #%d \n'%(pthread_id,lthread_pid,lthread_tid,lthread_id))
    output_file.close()
    
  def read_file(self,filename):
    """
    ____________________________________________________________________________
    
    Initialize the affinity from the verbose output written in a file
    Input:
    - fielname: file to be read
    ____________________________________________________________________________
    """
    with open(filename,'r') as file:
      file_content = file.readlines()
    self.nlines = len(file_content)
    print(' Opening of file:',filename)
    print(' Number of lines:',self.nlines)
    
    # Analyse file and put it in a dictionnary
    self.sort_by_info_number(file_content)
    
    # Get number of package, cores, threads
    self.get_packages()
    
    # Get initial proc set
    self.get_initial_proc_set()
    
    # Get proc map: threads ids and associated cores
    self.get_proc_map()
    
    # Get logical thread assignation
    self.get_thread_bindings()

  def plot(self,fig,ax):
    """
    Plot the results
    """

    colors = ['b','g','r','orange']

    for ip in range(self.npackages):
      # Creation of the arrays of each package
      cores = []
      threads = []
      lthreads = []
      for ic in range(self.package_list[ip].ncores):
        for it in range(self.package_list[ip].core_list[ic].nthreads):
          if (self.package_list[ip].core_list[ic].thread_list[it].lthread_pid > 0):
            cores.append(self.package_list[ip].coreid_list[ic])
            threads.append(self.package_list[ip].core_list[ic].thread_list[it].pthread_id)
            lthreads.append(self.package_list[ip].core_list[ic].thread_list[it].lthread_id)
      ax.scatter(cores,lthreads,color=colors[ip])
    

# ______________________________________________________________________________
# Class Package    

class Package:
  """
  """
  def __init__(self,ncores=0,nthreads=0):
    self.ncores = ncores     # Number of cores
    self.nthreads= nthreads  # number of threads per cores
    self.core_list = []      # list of cores
    self.coreid_list = []    # List of id related to the core of same index in core_list 

    self.proc_list = []           # Proc set as given by kmp affinity
    self.proctocore_list = []     # Core that own this proc at same index in proc_list 
    self.proctothread_list = []   # Thread that own this proc at same index in proc_list 

    for i in range(self.ncores) :
      core = Core(self.nthreads)
      self.core_list.append(core)
      
  def add_core(self,core_id,nthreads=0):
    core = Core(nthreads=nthreads)
    self.core_list.append(core) 
    self.coreid_list.append(core_id)
    self.ncores += 1   

# ______________________________________________________________________________
# Class Core

class Core:
  """
  """
  def __init__(self,nthreads=0):
    self.nthreads = nthreads  # Number of threads
    self.thread_list = []     # List of threads

    for i in range(nthreads) :
      thread = Thread()
      self.thread_list.append(thread)  
      
  def add_thread(self,pthread_id=0):
    thread = Thread(pthread_id = pthread_id)
    self.thread_list.append(thread)
    self.nthreads +=1
    
  def update_thread(self,index,pthread_id=None):
    if (pthread_id != None):
      self.thread_list[index].pthread_id = pthread_id

# ______________________________________________________________________________
# Class Thread

class Thread:
  def __init__(self,pthread_id=0,lthread_pid=0,lthread_tid=0,lthread_id=0):
    self.pthread_id = pthread_id      # physical thread id
    self.lthread_pid = lthread_pid    # pid associated to the thread
    self.lthread_tid = lthread_tid    # tid associated to the thread
    self.lthread_id = lthread_id      # logical thread id
    
