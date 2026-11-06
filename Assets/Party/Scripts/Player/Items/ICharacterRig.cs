using System;
using UnityEngine;

namespace Alarma.Player.Items
{
    // Huesos que necesita sostener un objeto: el pecho (de dónde se ubica) y los dos brazos hasta la palma.
    // Cambian cuando el personaje cambia de cuerpo (por ejemplo, de rol); entonces se avisa con RigChanged.
    public interface ICharacterRig
    {
        Transform Root { get; }
        Transform Chest { get; }
        // Columna baja (abdomen): las acciones inclinan y giran el torso desde aquí.
        Transform Spine { get; }
        Transform RightUpperArm { get; }
        Transform RightLowerArm { get; }
        Transform RightPalm { get; }
        Transform LeftUpperArm { get; }
        Transform LeftLowerArm { get; }
        Transform LeftPalm { get; }
        bool HandsBusy { get; }
        event Action RigChanged;
    }
}
