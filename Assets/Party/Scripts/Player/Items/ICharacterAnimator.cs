using System;
using UnityEngine;

namespace Alarma.Player.Items
{
    // El Animator del cuerpo que se ve, para el componente que reproduce los clips de uso de objetos (ItemActionAnimator).
    // Cambia cuando el personaje cambia de cuerpo (por ejemplo, de rol); entonces se avisa con RigChanged.
    public interface ICharacterAnimator
    {
        Animator Animator { get; }
        event Action RigChanged;
    }
}
