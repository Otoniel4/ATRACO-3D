// El tipo se mantiene en un archivo del mismo nombre para poder asignarlo como componente en Unity.
namespace Alarma.AI.CityLife
{
    public sealed class LocalCityLifeAuthority : CityLifeAuthority
    {
        public override bool CanSimulate => enabled;
    }
}
