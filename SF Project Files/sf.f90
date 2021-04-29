program sf

  use sf_subs
  use stream_subs

  implicit none

  ! The lightcurve.
  integer :: npts
  type(a_point), dimension(:), allocatable :: curve
  real :: medval_flux, mean
  double precision :: tlong

  ! The structure function.
  double precision :: first_bound
  double precision, allocatable, dimension(:) :: bound
  integer :: nbound, ibound
  integer :: ifirst, isecond
  real :: deltat
  real :: rep_fudge
  ! The values of x as defined in the paper.
  real, allocatable, dimension(:) :: xlist
  integer, allocatable, dimension(:) :: used
  integer :: ilist, iused
  real :: sf_value, sf_noise

  character(len=100) :: filout
  integer :: idot

  ! Set this to 1.5d+00 to reproduce Darryl's results.
  double precision, parameter :: bin_ratio=1.5d+00
  ! Do you want to define the first step as Darryl did
  ! (0.005 days), or let the lightcurve time tags do it (-1.0d0).
  ! double precision :: first_ts=0.005
  double precision :: first_ts=-1.0d0

  open(unit=12, file='files.txt')

  do

  call read_clean_lc(curve, npts)

  if (npts > 1) then

    ! Find the median.
    medval_flux=median(curve(1:npts)%col%data)
    print*, 'Median ', medval_flux

    ! Set up the bin boundaries.  The first constraint is that the step
    ! between the bin boundaries is a factor bin_ratio.  There are two ways of
    ! setting the bin boundaries.  Using the data we deamnd that the
    ! geometric mean of the first two boundaries is the shortest time step.
    ! Alternatively we set it to 0.05 days, to match Darryl's SF.
    if (first_ts < 0.0d0) then
      ! As the lightcurve may not be time ordered.
      first_ts=abs(curve(1)%bjd-curve(2)%bjd)
      do ifirst=1, npts
        do isecond=1, npts
          if (ifirst /= isecond) then
            first_ts=min(first_ts, dble(abs(curve(isecond)%bjd-curve(ifirst)%bjd)))
          end if
        end do
      end do
    end if
    ! Longest possible step is the length of the data, so number required is...
    first_bound=first_ts/dsqrt(bin_ratio)
    tlong=first_ts
    do ifirst=1, npts
      do isecond=1, npts
        if (ifirst /= isecond) then
          tlong=max(tlong, dble(abs(curve(isecond)%bjd-curve(ifirst)%bjd)))
        end if
      end do
    end do
    print*, 'Longest timescale is ', tlong
    nbound=int(log(tlong/first_bound)/log(bin_ratio))+3
    ! print*, curve(npts)%bjd, first_bound, nbound
    allocate(bound(nbound))
    bound(1)=first_bound
    do ibound=2, nbound
      bound(ibound)=bound(ibound-1)*bin_ratio
    end do

    ! write(*,10) bound
10  format(f12.7)

    allocate(xlist(npts*npts), used(npts))

    call lstfilin(filout)
    idot=index(filout, '.', back=.true.)
    open (unit=24, file=filout(1:idot)//'sf')
    write(24,*) '#'
    write(24,*) '# MEDIAN FLUX = ', medval_flux
    write(24,*) '# TIME SF SF_UNCER N_EFF MEAN_X'
    ! Now calculate the structure function.
    do ibound=1, nbound-1
      ilist=0
      used=0
      do ifirst=1, npts-1
        do isecond=ifirst+1, npts
          deltat=curve(isecond)%bjd-curve(ifirst)%bjd
          if (deltat > bound(ibound) .and. deltat <= bound(ibound+1)) then
            ilist=ilist+1
            used(ifirst)=used(ifirst)+1
            used(isecond)=used(isecond)+1
            xlist(ilist)=curve(ifirst)%col%data-curve(isecond)%col%data
          end if
        end do
      end do
      ! Divide the difference in fluxes by the median value.
      xlist(1:ilist)=xlist(1:ilist)/medval_flux
      ! Throw out anything with just one pair.
      if (ilist > 1) then
        sf_value=sum(xlist(1:ilist)**2.0)/real(ilist)
        mean=sum(xlist(1:ilist))/real(ilist)
        ! What about the uncertainty?
        ! Do what it says in the paper!
        ! First count the number of lightcurve points used.
        iused=count(used > 0)
        ! Now calculate the fudge factor (D) for how often a point is re-used.
        rep_fudge=(real(maxval(used))/median(real(pack(used, used >0))))**(1.0/3.0)
        ! rep_fudge=1.0
        ! And hence calculate the noise.
        sf_noise=rep_fudge*sqrt(sum((xlist(1:ilist)**2.0-sf_value)**2.0)/real(ilist))/&
        sqrt(real(iused))
        write(24,*) real(sqrt(bound(ibound)*bound(ibound+1))), sf_value, &
        sf_noise, real(iused)/(rep_fudge*rep_fudge), mean
      end if

    end do
    close(24)
    close(23)
    deallocate(bound, xlist, used)

  else

    print*, 'Less than two good data points in file.  No output written.'

  end if

  end do

end program sf
