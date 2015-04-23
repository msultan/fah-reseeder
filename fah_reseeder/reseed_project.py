import mdtraj as mdt
import os
import numpy as np
from mdtraj.utils.contextmanagers import enter_temp_directory
import glob
import tarfile
from simtk.openmm import *
from simtk.openmm import app
import simtk.openmm as mm


def create_simulation_obj(old_state, system, integrator):
    platform = mm.Platform.getPlatformByName('Reference')
    simulation = app.Simulation(old_state, system, integrator, platform)
    return simulation


def serializeObject(proj_folder, run_index, obj, objname):
    file_name = proj_folder + "/new_project/RUN%d/" % (run_index) + objname
    print file
    objfile = open(file_name, 'w')
    objfile.write(XmlSerializer.serialize(obj))
    objfile.close()


def load_setup_files(proj_folder, traj_fname):
    # 0_0.hd5 is run 0 clone 0
    run_index = int(traj_fname.split("_")[0])

    print run_index
    glob_input = proj_folder + "/RUN%d/CLONE0/payload-*.tar.bz2" % run_index
    print glob_input
    payload_file = glob.glob(glob_input)[0]

    print payload_file
    if not payload_file:
        raise "Error:Payload files not found"

    print os.path.abspath(payload_file)
    with enter_temp_directory():
        archive = tarfile.open(payload_file, mode='r:bz2')
        archive.extract("system.xml")
        archive.extract("integrator.xml")
        archive.extract("state.xml")

        with open("state.xml") as state_input:
            state = XmlSerializer.deserialize(state_input.read())
        with open("system.xml") as system_input:
            system = XmlSerializer.deserialize(system_input.read())
        with open("integrator.xml") as integrator_input:
            integrator = XmlSerializer.deserialize(integrator_input.read())

    return state, system, integrator


def pull_new_seeds(proj_folder, top_folder, cluster_mdl, assignments, n_runs, n_clones, stride):
    try:
        os.mkdir(proj_folder + "/new_project")
    except:
        pass
    try:
        os.mkdir(proj_folder + "/new_project/topologies")
    except:
        pass


    # creating an old fashioned assignments array to make using np.choice easier
    max_traj_length = np.max([len(assignments[i][0]) for i in assignments.keys()])
    n_trajs = len(assignments.keys())

    assignment_array = np.zeros((n_trajs, max_traj_length)) - 1

    mapping_dict = {}

    state_counts_list = np.zeros(cluster_mdl.n_clusters)

    for i, v in enumerate(assignments.keys()):
        assignment_array[i][:len(assignments[v][0])] = assignments[v][0]
        mapping_dict[i] = v

    for i in range(cluster_mdl.n_clusters):
        state_counts_list[i] = np.count_nonzero(assignment_array == i)

    print n_runs
    sorted_cluster_indices = np.argsort(state_counts_list)[:n_runs]
    print sorted_cluster_indices
    for ind, val in enumerate(sorted_cluster_indices):
        try:
            os.mkdir(proj_folder + "/new_project/RUN%d" % ind)
        except:
            pass

        #get where the state exists
        traj_ind, frame_ind = np.where(assignment_array == val)

        #get a random choice
        chosen_ind = np.random.choice(range(len(traj_ind)))

        print traj_ind, frame_ind
        #get trajectory name and frame index
        traj_fname = mapping_dict[traj_ind[chosen_ind]]
        frame_ind = frame_ind[chosen_ind]

        print traj_fname, frame_ind
        #basic sanity test
        assert (assignments[traj_fname][0][frame_ind] == val)

        top = os.path.join(top_folder+"/%s.pdb" % os.path.basename(traj_fname).split("_")[0])

        #since we use stride, multiple frame_ind with stride rate to get actual frame index.
        new_state = mdt.load_frame(proj_folder + "/trajectories/%s" % traj_fname, top=top, index=frame_ind * stride)

        #save it for later reference
        new_state.save_pdb(proj_folder + "/new_project/topologies/%d.pdb" % ind)
        #load pdb in openmm format


        old_state, system, integrator = load_setup_files(proj_folder, traj_fname)

        simulation = create_simulation_obj(old_state, system, integrator)

        #set new positions
        pdb = app.PDBFile(proj_folder + "/new_project/topologies/%d.pdb" % ind)
        simulation.context.setPositions(pdb.positions)

        #serialize system and integrator once
        serializeObject(proj_folder, ind, system, 'system.xml')
        serializeObject(proj_folder, ind, integrator, 'integrator.xml')

        #basic sanity test that the number of atoms are the same. should add more tests
        assert (simulation.system.getNumParticles() == new_state.n_atoms == system.getNumParticles())

        for j in range(n_clones):
            simulation.context.setVelocitiesToTemperature(300)
            current_state = simulation.context.getState(getPositions=True, getVelocities=True, \
                                                        getForces=True, getEnergy=True, getParameters=True,
                                                        enforcePeriodicBox=True)
            serializeObject(proj_folder, ind, current_state, 'state%d.xml' % j)



